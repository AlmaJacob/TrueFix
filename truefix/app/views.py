from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Category, Service, Booking
from django.contrib.auth.models import User
import os

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
        return render(req, 'user/view_bookings.html', {'bookings': bookings})
    return redirect(service_login)

def cancel_booking(req, booking_id):
    if 'user' in req.session:
        booking = Booking.objects.get(pk=booking_id)
        booking.status = 'cancelled'
        booking.save()
        return redirect(user_bookings)
    return redirect(service_login)


def contact(req):
    if req.method == 'POST':
        name = req.POST['name']
        email = req.POST['email']
        phone = req.POST['phone']
        message = req.POST['message']
        try:
            data = contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message
            )
            data.save()
            return render(req, 'user/contact.html')
        except Exception as e:
            return render(req,'user/contact.html')
    
    return render(req,'user/contact.html')

def about(req):
    return render(req,'user/about.html')

def blog(req):
    return render(req,'user/blog.html')

def user_bookings(req):
    buy = Booking.objects.all()[::-1]
    return render(req, 'user/service.html', {'buy': buy})

# def buy_pro(req, id):
#     product = Product.objects.get(pk=id)
#     user = User.objects.get(username=req.session['user'])
#     price = product.offer_price
#     qty = 1
#     data = Buy.objects.create(user=user, product=product, qty=qty, price=price)
#     data.save()
#     return redirect(view_bookings)


def view_service(req,pid):
    cat=Category.objects.get(pk=pid)
    print(cat)
    service=Service.objects.filter(category=cat)
    return render(req,'user/view_service.html',{'service':service})