from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *
import os
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Service, Appointment, Payment


# Create your views here.

def company_login(req):
    if 'company' in req.session:
        return redirect(company_home)
    if 'user' in req.session:
        return redirect(company_home)
    else:
        if req.method=='POST':
            uname=req.POST['uname']
            password=req.POST['password']
            data=authenticate(username=uname,password=password)
            if data:
                login(req,data)
                if data.is_superuser:
                    req.session['company']=uname     #create
                    return redirect(company_home)
                else:
                    req.session['user']=uname
                    return redirect(company_home)
            else:
                messages.warning(req, "Invalid Username or Password")
                return redirect(company_login)
    return render(req,'login.html')

def company_logout(req):
    logout(req)
    req.session.flush()
    return redirect(company_login)

def register(req):
    if req.method=='POST':
        uname=req.POST['uname']
        email=req.POST['email']
        password=req.POST['password']

        try:
            data=User.objects.create_user(first_name=uname,email=email,
                                        username=email,password=password)
            data.save()
        except:
            messages.warning(req, "Username or Email already exist")
            return redirect(register)
        return redirect(company_login)
    else:
        return render(req,'register.html')
    
    #---------company--------------

def company_home(req):
    if 'company' in req.session:
        return render(req,'shop/shop_home.html')
    else:
        return redirect(company_login)
    


# ------------------USER------------------------------------------------

def user_home(req):
    return render(req, 'user/user_home.html')

def service_list(request):
    services = Service.objects.all()
    return render(request, 'service/service_list.html', {'services': services})

# View for creating an appointment
def create_appointment(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    # logic to create an appointment (simplified for this example)
    if request.method == 'POST':
        # Handle form submission, create an Appointment
        # Assume we have a logged-in customer
        appointment = Appointment.objects.create(
            customer=request.user.customer,
            service=service,
            appointment_date=request.POST['appointment_date'],
            status='Pending'
        )
        return render(request, 'service/appointment_success.html', {'appointment': appointment})

    return render(request, 'service/create_appointment.html', {'service': service})