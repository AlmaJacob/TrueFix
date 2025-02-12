from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Service, Booking
from .forms import BookingForm

# Create your views here.

def shop_login(req):
    if 'shop' in req.session:
        return redirect(shop_home)
    if 'user' in req.session:
        return redirect(user_home)
    else:
        if req.method=='POST':
            uname=req.POST['uname']
            password=req.POST['password']
            data=authenticate(username=uname,password=password)
            if data:
                login(req,data)
                if data.is_superuser:
                    req.session['shop']=uname     #create
                    return redirect(shop_home)
                else:
                    req.session['user']=uname
                    return redirect(user_home)
            else:
                messages.warning(req, "Invalid Username or Password")
                return redirect(shop_login)
    return render(req,'login.html')

def shop_logout(req):
    logout(req)
    req.session.flush()
    return redirect(shop_login)

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
        return redirect(shop_login)
    else:
        return render(req,'register.html')
    

def home(request):
    categories = Category.objects.all()
    featured_services = Service.objects.filter(is_available=True)[:6]
    return render(request, 'services/home.html', {
        'categories': categories,
        'featured_services': featured_services
    })

def service_list(request, category_id=None):
    if category_id:
        services = Service.objects.filter(category_id=category_id, is_available=True)
        category = Category.objects.get(id=category_id)
    else:
        services = Service.objects.filter(is_available=True)
        category = None
    
    return render(request, 'services/service_list.html', {
        'services': services,
        'category': category
    })

def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'services/service_detail.html', {'service': service})

@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.service = service
            booking.save()
            messages.success(request, 'Booking submitted successfully!')
            return redirect('dashboard')
    else:
        form = BookingForm()
    
    return render(request, 'services/booking.html', {
        'form': form,
        'service': service
    })

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/dashboard.html', {'bookings': bookings})
