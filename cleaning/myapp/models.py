from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta, datetime



# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('staff', 'Staff'),
#         ('is_cleaner', 'Cleaner'),
#         ('user', 'User'),
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
#     def __str__(self):
#         return f"{self.username} ({self.role})"

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('staff', 'Staff'),
        ('is_cleaner', 'Cleaner'),
        ('user', 'User'),
        ('admin', 'Admin'),  # Added Admin role
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    registered_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_users'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
