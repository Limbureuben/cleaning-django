from django.db import models # type: ignore
from django.contrib.auth.models import User

class Organization(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizations')
    organization_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=100)
    services = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')


class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    requested_at = models.DateTimeField(auto_now_add=True)


class Cleaner(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('inactive', 'Inactive'),
        ('busy', 'Busy'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # staff who registered the cleaner
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.full_name} - {self.status}"
