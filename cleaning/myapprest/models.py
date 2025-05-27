import uuid
from django.db import models

# Create your models here.
class Company(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    company_name= models.CharField(max_length=100,null=False,blank=False)
    region_located=models.CharField(max_length=100,null=False,blank=False)
    location=models.CharField(max_length=50,null=False,blank=False)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="price  for a service, can be overridden by service rates."
    )
    discount = models.PositiveIntegerField(default=0, help_text="Discount percentage if applicable.")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    available_date = models.DateField()
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    # logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.company_name
    

class Employee(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    employee_name = models.CharField(max_length=255)
    employee_email = models.EmailField()
    employee_phone = models.CharField(max_length=20)
    employee_role = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.employee_name
class Service(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255) 
    hourly_rate = models.DecimalField(max_digits=7, decimal_places=2)
    estimated_duration = models.IntegerField(help_text="Duration in hours", null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
class Customer(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(unique=True)
    customer_phonenumber = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.customer_name
    
class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    service = models.ManyToManyField(Service)
    date = models.DateField()
    time = models.TimeField()
    hours_requested = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.customer_name} - {self.services} - {self.date}"
class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.customer_name} - {self.company.name} - {self.rating}"