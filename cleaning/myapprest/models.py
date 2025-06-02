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