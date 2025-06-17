from django.db import models # type: ignore
from django.contrib.auth.models import User

class Organization(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )

    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizations')
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Replaced email
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True)
    file = models.FileField(upload_to='organization_files/', null=True, blank=True)
    services = models.CharField(max_length=500)
    bedrooms = models.CharField(max_length=10, null=True)
    guests = models.CharField(max_length=10, null=True)
    bathrooms = models.CharField(max_length=10, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')



class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    requested_at = models.DateTimeField(auto_now_add=True)


# class Cleaner(models.Model):
#     STATUS_CHOICES = [
#         ('available', 'Available'),
#         ('assigned', 'Assigned'),
#         ('inactive', 'Inactive'),
#         ('busy', 'Busy'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=100)
#     location = models.CharField(max_length=100, null=True)
#     contact = models.CharField(max_length=20)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

#     def __str__(self):
#         return f"{self.full_name} - {self.status}"



class Cleaner(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('inactive', 'Inactive'),
        ('busy', 'Busy'),
    ]

    registered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_cleaners')
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cleaner_profile')
    full_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True)
    contact = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.full_name} - {self.status}"
