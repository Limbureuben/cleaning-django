from django.db import models # type: ignore
from django.contrib.auth.models import User
from myapp.models import *
from django.conf import settings

class Organization(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )

    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizations')
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


# models.py

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('available', 'available'),
        ('taken', 'Taken'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='available'
    )

    def __str__(self):
        return f"{self.username} ({self.status})"



class Cleaner(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('inactive', 'Inactive'),
        ('busy', 'Busy'),
    ]

    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='registered_cleaners')
    auth_user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='cleaner_profile')
    full_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True)
    contact = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.full_name} - {self.status}"



class CleanerRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cleaner_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    service_request = models.ForeignKey('ServiceRequest', null=True, on_delete=models.CASCADE)  # ✅ NEW
    cleaner_location = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} → {self.service_request} ({self.status})"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"



# class CleanerRating(models.Model):
#     cleaner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received')
#     client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_given')
#     service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE)
#     rating = models.PositiveIntegerField()  # 1 to 5
#     comment = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.client.username} → {self.cleaner.username} ({self.rating})"


class CleaningReport(models.Model):
    cleaner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cleaning_reports')
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='cleaning_reports')
    description = models.TextField()
    completed_at = models.DateField()
    attachment = models.FileField(upload_to='cleaning_reports/', null=True, blank=True)
    client_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # Rating out of 5?

    def __str__(self):
        return f"Report by {self.cleaner.username} on Request #{self.service_request.id}"
