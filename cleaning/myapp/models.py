from django.db import models

# Create your models here.

class Organization(models.Model):
    organization_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=100)
    service = models.CharField(max_length=500)