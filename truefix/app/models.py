from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer') 
    phone = models.CharField(max_length=15)
    address = models.TextField()
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.user.username

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    phone = models.CharField(max_length=15)
    hire_date = models.DateField()

    def __str__(self):
        return self.user.username


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Service(models.Model):
    img=models.FileField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')  # Link to ServiceCategory

    def __str__(self):
        return self.name

class Appointment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='appointments')  # Link to Employee
    appointment_date = models.DateTimeField()
    status_choices = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')

    def __str__(self):
        return f"Appointment for {self.customer.user.username} on {self.appointment_date}"


class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method_choices = [
        ('Credit Card', 'Credit Card'),
        ('Cash', 'Cash'),
        ('Online', 'Online'),
    ]
    payment_method = models.CharField(max_length=20, choices=payment_method_choices)

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.appointment}"

class ServiceReview(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    rating_choices = [(i, i) for i in range(1, 6)]  
    rating = models.IntegerField(choices=rating_choices)
    review = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.service.name} by {self.customer.user.username}"
