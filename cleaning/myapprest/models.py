from django.db import models # type: ignore
from django.contrib.auth.models import User

class Organization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizations')
    organization_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=100)
    service = models.CharField(max_length=500)