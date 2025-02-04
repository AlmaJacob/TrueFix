from django.contrib import admin
from .models import Customer, Employee, Service, ServiceCategory, Appointment, Payment, ServiceReview

admin.site.register(Customer)
admin.site.register(Employee)
admin.site.register(Service)
admin.site.register(ServiceCategory)
admin.site.register(Appointment)
admin.site.register(Payment)
admin.site.register(ServiceReview)

