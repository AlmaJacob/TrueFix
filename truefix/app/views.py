from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from .models import *
from django.contrib.auth.models import User
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import razorpay
import json 
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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


def cancel_order(req, order_id):
    order = get_object_or_404(Booking, pk=order_id)
    order.delete()
    return redirect(view_bookings)


def confirm_order(request, order_id):
    order = get_object_or_404(Booking, pk=order_id)  # Correct model

    if order.status != "confirmed":  # Check status correctly
        order.status = "confirmed"  # Change status instead of is_confirmed
        order.save()

        if order.user and order.user.email:
            recipient_email = order.user.email
            print(f"Attempting to send email to: {recipient_email}")

            subject = "Order Confirmation"
            message = f"""
            Dear {order.user.first_name},

            Your order ({order.service.name}) has been confirmed.
            Thank you for shopping with us!

            Best regards,
            TrueFix
            """

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)
                print("Email sent successfully!")  
            except Exception as e:
                print(f"Email sending failed: {e}")  
        else:
            print("Error: User does not have an email address!")
    
    return redirect(view_bookings)  # Redirect correctly

# def confirm_order(request, order_id):
#     # order = get_object_or_404(Service, pk=order_id)
#     order = get_object_or_404(Booking, pk=order_id)  # Use the correct model

#     if not order.is_confirmed:
#         order.is_confirmed = True
#         order.save()

#         if not order.user or not order.user.email:
#             print("Error: User does not have an email address!")
#             return redirect('admin_bookings')  

#         recipient_email = order.user.email
#         print(f"Attempting to send email to: {recipient_email}")  

#         subject = "Order Confirmation"
#         message = f"""
#         Dear {order.user.first_name},

#         Your order ({order.service.name}) has been confirmed.
#         Thank you for shopping with us!

#         Best regards,
#         Dreamy Delights Team
#         """

#         try:
#             send_mail(
#                 subject,
#                 message,
#                 settings.EMAIL_HOST_USER,
#                 [recipient_email],  
#                 fail_silently=False,
#             )
#             print("Email sent successfully!")  
#         except Exception as e:
#             print(f"Email sending failed: {e}")  

#     return redirect(view_bookings)

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

def cancel_booking(request, bid):
    # Get the booking only if it belongs to the logged-in user
    booking = get_object_or_404(Booking, pk=bid, user=request.user)

    # Update booking status
    booking.status = 'cancelled'
    booking.save()

    return redirect('user_bookings')
  # Redirect after cancellation
    

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

# def buy_now(req, id):
#     service = get_object_or_404(Service, pk=id)
#     user = User.objects.get(username=req.session['user'])
#     addresses = Address.objects.filter(user=user).order_by('-id')  # Fetch all addresses for the user
    
#     if req.method == 'POST':
#         booking_date = req.POST['booking_date']
#         booking_time = req.POST['booking_time']
#         special_requests = req.POST.get('special_requests', '')
#         selected_address_id = req.POST.get('address')

#         if selected_address_id:
#             selected_address = Address.objects.get(id=selected_address_id, user=user)
#         else:
#             selected_address = None  # Handle case where no address is selected

#         Booking.objects.create(
#             user=user, 
#             service=service, 
#             booking_date=booking_date, 
#             booking_time=booking_time, 
#             special_requests=special_requests,
#             address=selected_address  # Store selected address
#         )

#         req.session['service'] = id
#         req.session['booking'] = id
#         req.session['amount'] = id
#         return redirect('order_payment')  # Redirect to payment page on form submission

#     return render(req, 'user/buy_now.html', {'service': service, 'addresses': addresses})

# def buy_now(req,id):
#     service = get_object_or_404(Service, pk=id)
#     user=User.objects.get(username=req.session['user'])
#     address = Address.objects.filter(user=req.user).order_by('-id').first()  # Fetch the user's address
#     if req.method == 'POST':
#             booking_date = req.POST['booking_date']
#             booking_time = req.POST['booking_time']
#             special_requests = req.POST.get('special_requests', '')
#             Booking.objects.create(user=user, service=service, booking_date=booking_date, booking_time=booking_time, special_requests=special_requests)
#             req.session['service']=id
#             req.session['booking']=id
#             req.session['amount']=id
#             return redirect('order_payment')  # Redirect to payment page on form submission

#     return render(req, 'user/buy_now.html', {'service': service, 'address': address})
def buy_now(req, id):
    service = get_object_or_404(Service, pk=id)
    user = req.user  # ✅ Fetch user from request instead of session
    
    # Fetch all addresses of the user
    addresses = Address.objects.filter(user=user).order_by('-id')  
    
    if req.method == 'POST':
        booking_date = req.POST['booking_date']
        booking_time = req.POST['booking_time']
        special_requests = req.POST.get('special_requests', '')
        address_id = req.POST.get('address')  # Fetch selected address from form
        
        if not address_id:
            messages.error(req, "Please select an address.")
            return redirect('buy_now', id=id)

        # Get the selected address
        address = get_object_or_404(Address, id=address_id, user=user)  # ✅ Ensures only user's address is fetched

        # Create the booking
        booking = Booking.objects.create(
            user=user,
            service=service,
            booking_date=booking_date,
            booking_time=booking_time,
            special_requests=special_requests,
            address=address,  # ✅ Save selected address
        )
        
        # Store necessary data in session
        req.session['service'] = id
        req.session['booking'] = booking.id  # ✅ Store correct booking ID
        req.session['amount'] = float(service.price)  # ✅ Convert to float for serialization

        return redirect('order_payment')  # Redirect to payment page

    return render(req, 'user/buy_now.html', {'service': service, 'addresses': addresses})  # Pass all addresses

def payment_page(request,pid):
    return render(request, 'user/payment.html') 

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




# def order_success(request):
#     return render(request, 'user/order_success.html')

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



# def user_profile(req):
#   return render(req, "user/user_profile.html")

# def user_profile(request):
#     Profile = profile.objects.filter(user=request.user).first()  

#     return render(request, 'user/user_profile.html', {'profile': Profile})
    
def user_profile(request):
    user_profile, created = profile.objects.get_or_create(user=request.user)
    return render(request, 'user/user_profile.html', {'profile': user_profile})


def update_profile(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get("first_name", "").strip()
        username = request.POST.get("username", "").strip()

        if not first_name or not username:
            messages.error(request, "Both fields are required.")
            return render(request, "user/profile.html", {"user": user})

        try:
            validate_email(username)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return render(request, "user/profile.html", {"user": user})

        if user.username != username and user.__class__.objects.filter(username=username).exists():
            messages.error(request, "This email is already in use.")
            return render(request, "user/profile.html", {"user": user})

        user.first_name = first_name
        user.username = username
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect(user_profile)

    return render(request, "user/profile.html", {"user": request.user})

@login_required

def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('service_login')
    
    return render(request, "user/user_profile.html")




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
                return redirect(user_bookings)
            else:
                # If signature verification fails, mark the payment as failed
                order.status = "failed"
                order.save()
                return JsonResponse({"error": "Payment verification failed"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
    


def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address_text = request.POST.get('address')
        phone = request.POST.get('phone')
        pincode = request.POST.get('pincode')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')

        if name and address_text and phone:
            address = Address.objects.create(
                user=request.user,
                name=name,
                address=address_text,
                phone=phone,
                pincode=pincode,
                street=street,
                state=state,
                city=city,

            )

            # Profile, created = profile.objects.get_or_create(user=request.user)
            # if not Profile.primary_address:
            #     Profile.primary_address = address
            #     Profile.save()
            user_profile, created = profile.objects.get_or_create(user=request.user)
            if not user_profile.primary_address:
                user_profile.primary_address = address
                user_profile.save()

            messages.success(request, "Address added successfully.")
            return redirect(user_profile)
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'user/profile.html')


def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        address_text = request.POST.get('address')
        phone = request.POST.get('phone')
        pincode = request.POST.get('pincode')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')

        if name and address_text and phone:
            address.name = name
            address.address = address_text
            address.phone = phone
            address.street = street
            address.state = state
            address.city = city
            address.pincode = pincode
            address.save()

            messages.success(request, "Address updated successfully.")
            return redirect(user_profile)
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'user/profile.html', {'address': address})


def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    Profile = get_object_or_404(profile, user=request.user)

    if Profile.primary_address == address:
        Profile.primary_address = None
        Profile.save()

    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect(user_profile)




    # order = get_object_or_404(Buy, pk=order_id)
    # order.delete()
    # return redirect("admin_bookings")


