from django.urls import path
from . import views

urlpatterns = [
    path('',views.shop_login),
    path('logout',views.shop_logout),
    path('register',views.register),
    path('', views.home, name='home'),
    path('services/', views.service_list, name='service_list'),
    path('services/category/<int:category_id>/', views.service_list, name='category_services'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('service/<int:service_id>/book/', views.book_service, name='book_service'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
