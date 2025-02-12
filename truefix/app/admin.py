
from django.contrib import admin
from .models import Category, Service, Booking

# Register your models here.

from django.contrib import admin
from .models import Category, Service, Booking

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'booking_date', 'booking_time', 'status']
    list_filter = ['status', 'booking_date']
    search_fields = ['user__username', 'service__name']