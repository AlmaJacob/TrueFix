from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail



from .models import Category, Service, Booking,Order
from django.contrib.auth.models import User
import os
from django.shortcuts import render, get_object_or_404, redirect
from .models import Service, Address 
from django.http import JsonResponse
from django.conf import settings
import razorpay
import json 
from django.views.decorators.csrf import csrf_exempt
# Authentication

def service_login(req):
    if 'company' in req.session:
        return redirect(company_home)
    if 'user' in req.session:
        return redirect(user_home)
    else:
        if req.method == 'POST':
            uname = req.POST['uname']
            password = req.POST['password']
            user = authenticate(username=uname, password=password)
            if user:
                login(req, user)
                if user.is_superuser:
                    req.session['company'] = uname
                    return redirect(company_home)
                else:
                    req.session['user'] = uname
                    return redirect(user_home)
            else:
                messages.warning(req, "Invalid Username or Password")
                return redirect(service_login)
    return render(req, 'login.html')

def service_logout(req):
    logout(req)
    req.session.flush()
    return redirect(service_login)

def register(req):
    if req.method == 'POST':
        uname = req.POST['uname']
        email = req.POST['email']
        password = req.POST['password']
        try:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=uname)
            user.save()
        except:
            messages.warning(req, "Username or Email already exists")
            return redirect(register)
        return redirect(service_login)
    return render(req, 'register.html')

# company Views

def company_home(req):
    if 'company' in req.session:
        services = Service.objects.all()
        return render(req, 'company/company_home.html', {'services': services})
    return redirect(service_login)

def add_service(req):
    if 'company' in req.session:
        if req.method == 'POST':
            category_id = req.POST['category']
            name = req.POST['name']
            description = req.POST['description']
            price = req.POST['price']
            image = req.FILES['image']
            category = Category.objects.get(pk=category_id)
            Service.objects.create(category=category, name=name, description=description, price=price, image=image)
            return redirect(company_home)
        categories = Category.objects.all()
        return render(req, 'company/add_service.html', {'categories': categories})
    return redirect(service_login)

def edit_service(req, sid):
    if 'company' in req.session:
        service = Service.objects.get(pk=sid)
        cat=Category.objects.all()
        if req.method == 'POST':
            service.name = req.POST['name']
            service.description = req.POST['description']
            service.price = req.POST['price']
            if 'image' in req.FILES:
                service.image = req.FILES['image']
            service.save()
            return redirect(company_home)
        return render(req, 'company/edit_service.html', {'service': service,'cat':cat})
    return redirect(service_login)

def delete_service(req, sid):
    if 'company' in req.session:
        service = Service.objects.get(pk=sid)
        os.remove(service.image.path)
        service.delete()
        return redirect(company_home)
    return redirect(service_login)

def view_bookings(req):
    if 'company' in req.session:
        bookings = Booking.objects.all().order_by('-created_at')
        return render(req, 'company/view_bookings.html', {'bookings': bookings})
    return redirect(service_login)

def update_booking_status(req, booking_id, status):
    if 'company' in req.session:
        booking = Booking.objects.get(pk=booking_id)
        booking.status = status
        booking.save()
        return redirect(view_bookings)
    return redirect(service_login)

# User Views

def user_home(req):
    services = Service.objects.all()
    category = Category.objects.all()
    return render(req, 'user/user_home.html', {'services': services,'cat':category})

def book_service(req, sid):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        service = Service.objects.get(pk=sid)
        if req.method == 'POST':
            booking_date = req.POST['booking_date']
            booking_time = req.POST['booking_time']
            special_requests = req.POST.get('special_requests', '')
            Booking.objects.create(user=user, service=service, booking_date=booking_date, booking_time=booking_time, special_requests=special_requests)
            return redirect(user_bookings)
        return render(req, 'user/order_bookings.html', {'service': service})
    return redirect(service_login)


def user_bookings(req):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        bookings = Booking.objects.filter(user=user)
        return render(req, 'user/bookings.html', {'bookings': bookings})
    return redirect('service_login')  # Redirect to login if the user isn't authenticated

def cancel_booking(req, bid):
    if 'user' in req.session:
        try:
            booking = Booking.objects.get(pk=bid, user__username=req.session['user'])  # Ensure it's the user's booking
            booking.status = 'cancelled'
            booking.save()
        except Booking.DoesNotExist:
            # Handle if booking doesn't exist or doesn't belong to the logged-in user
            return redirect('user_bookings')
        return redirect('user_bookings')  # After canceling, redirect to the bookings page
    return redirect('service_login') 
    

def contact(req):
    cat=Category.objects.all()
    if req.method == "POST":
        name = req.POST["name"]
        email = req.POST["email"]
        message = req.POST["message"]

        send_mail(
            subject=f"New Contact Form Submission from {name}",
            message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=email,
            recipient_list=["almajacob7@gmail.com"], 
            fail_silently=True,
        )

        messages.success(req, "Your message has been sent successfully!")
        return redirect(contact )  
    return render(req,'user/contact.html',{"cat":cat})


def about(req):
    return render(req,'user/about.html')

def blog(req):
    return render(req,'user/blog.html')


# def buy_pro(req, id):
#     product = Product.objects.get(pk=id)
#     user = User.objects.get(username=req.session['user'])
#     price = product.offer_price
#     qty = 1
#     data = Buy.objects.create(user=user, product=product, qty=qty, price=price)
#     data.save()
#     return redirect(view_bookings)


def buy_now(req,id):
    service = get_object_or_404(Service, pk=id)
    user=User.objects.get(username=req.session['user'])
    address = Address.objects.filter(user=req.user).order_by('-id').first()  # Fetch the user's address
    if req.method == 'POST':
            booking_date = req.POST['booking_date']
            booking_time = req.POST['booking_time']
            special_requests = req.POST.get('special_requests', '')
            Booking.objects.create(user=user, service=service, booking_date=booking_date, booking_time=booking_time, special_requests=special_requests)
            req.session['service']=id
            req.session['booking']=id
            req.session['amount']=id
            return redirect('order_payment')  # Redirect to payment page on form submission

    return render(req, 'user/buy_now.html', {'service': service, 'address': address})

# def payment_page(request,pid):
#     return render(request, 'user/payment.html') 
def order_payment(req):
    if 'user' in req.session:
        user = get_object_or_404(User, username=req.session['user'])

        # Retrieve session data
        service_id = req.session.get('service')
        booking_id = req.session.get('booking')

        if not service_id or not booking_id:
            return redirect('home')  # Redirect if session data is missing

        service = get_object_or_404(Service, pk=service_id)
        booking = get_object_or_404(Booking, pk=booking_id)

        total_amount = service.price  

        # Initialize Razorpay client
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": int(total_amount * 100),  # Convert to paise
            "currency": "INR",
            "payment_capture": "1"
        })

        # Create Order object in Django
        order = Order.objects.create(
            booking=booking,
            amount=service,  # Using Service instead of amount
            provider_order_id=razorpay_order['id'],
            payment_id="",
            signature_id="",
        )

        req.session['order_id'] = order.pk  

        return render(req, "user/payment.html", {
            "callback_url": "http://127.0.0.1:8000/callback/",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order": order,
            "user": user,
        })
    
    return redirect('login')  


def order_success(request):
    return render(request, "user/order_success.html")

def search_service(request):
    query = request.GET.get('q', '')  
    results = Service.objects.filter(name__icontains=query)
    cat=Category.objects.all()
    return render(request, 'user/search_results.html', {'query': query, 'results': results,"cat":cat})

def view_service(req,pid):
    cat=Category.objects.get(pk=pid)
    print(cat)
    service=Service.objects.filter(category=cat)
    return render(req,'user/view_service.html',{'service':service})



def user_profile(req):
  return render(req, "user/user_profile.html")
    


def update_username(request):
    if request.method == "POST":
        new_first_name = request.POST.get("name")
        new_username = request.POST.get("username")

        
        if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            messages.error(request, "This username is already taken. Please choose another one.")
            return redirect(user_profile) 

        
        if new_first_name and new_username:
            request.user.first_name = new_first_name
            request.user.username = new_username
            request.user.save()
            messages.success(request, "Username updated successfully!")
        else:
            messages.error(request, "Username and Name cannot be empty.")

    return redirect(user_profile)


@csrf_exempt
def callback(request):
    if request.method == "POST":
        try:
            # Extract Razorpay payment details from the POST request
            payment_id = request.POST.get("razorpay_payment_id")
            order_id = request.POST.get("razorpay_order_id")
            signature = request.POST.get("razorpay_signature")

            # Retrieve the order from your database
            order = Order.objects.get(provider_order_id=order_id)

            # Verify the signature using Razorpay's API
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            response = razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # If the signature is verified, we update the payment status and redirect to the success page
            if response:
                order.payment_id = payment_id
                order.signature_id = signature
                order.status = "paid"  # mark the order as paid
                order.save()

                # Redirect to the order success page
                return redirect('order_success')
            else:
                # If signature verification fails, mark the payment as failed
                order.status = "failed"
                order.save()
                return JsonResponse({"error": "Payment verification failed"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
    

def address(req):
    if 'user' in req.session:
        user=User.objects.get(username=req.session['user'])
        data=Address.objects.filter(user=user)
        if req.method=='POST':
            user=User.objects.get(username=req.session['user'])
            name=req.POST['name']
            phn=req.POST['phone']
            house=req.POST['address']
            street=req.POST['street']
            city=req.POST['city']
            pin=req.POST['pin']
            state=req.POST['state']
            data=Address.objects.create(user=user,name=name,phone=phn,address=house,city=city,street=street,pincode=pin,state=state)
            data.save()
            return redirect(address)
        else:
            return render(req,"user/user_profile.html",{'data':data})
    else:
        return redirect(service_login)

