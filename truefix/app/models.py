from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from .constants import PaymentStatus

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='categories/')
    
    def _str_(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # image = models.ImageField(upload_to='services/')
    image = models.ImageField(upload_to='services/',null=True)
    is_available = models.BooleanField(default=True)
    
    def _str_(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    special_requests = models.TextField(blank=True, null=True)
    
    def _str_(self):
        return f"{self.user.username} - {self.service.name}"
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.TextField()
    address=models.TextField()
    street=models.TextField()
    city=models.TextField()
    state=models.TextField()
    pincode=models.IntegerField()
    phone=models.IntegerField()

class Contact(models.Model):
    name = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()

class Order(models.Model):
    # name= CharField(_("Customer Name"), max_length=254, blank=False, null=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    # amount=models.IntegerField(_("Account"),null=False, blank=False)
    amount = models.ForeignKey(Service, on_delete=models.CASCADE)
    status=CharField(
        _("Payment_Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False
    )
    provider_order_id =models.CharField(
        _("order ID"), max_length=40, null=False, blank=False
    )
    payment_id =models.CharField(
        _("order ID"), max_length=36, null=False, blank=False
    )
    signature_id =models.CharField(
        _("order ID"), max_length=128, null=False, blank=False
    )

    def _str_(self):
        return f"{self.id}-{self.name}-{self.status}"