from django.contrib import admin
from .models import *

# Register your models here.
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('location', 'price', 'address', 'services', 'user', 'phone', 'status', 'guests', 'bedrooms', 'bathrooms', 'file')
    search_fields = ('location', 'price')
admin.site.register(Organization, OrganizationAdmin)

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'username', 'email', 'phone', 'start_date', 'end_date', 'status')
    search_fields = ('organization', 'username')
admin.site.register(ServiceRequest, ServiceRequestAdmin)



class CleanerAdmin(admin.ModelAdmin):
    list_display = ('registered_by', 'auth_user', 'full_name', 'contact', 'location', 'contact', 'status')
    search_fields = ('registered_by', 'full_name')
admin.site.register(Cleaner, CleanerAdmin)

class CleanerRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'service_request', 'cleaner_location', 'username', 'email')
    search_fields = ('from_user', 'to_user', 'service_request', 'username')
admin.site.register(CleanerRequest, CleanerRequestAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user', 'message')
admin.site.register(Notification, NotificationAdmin)


class CleaningReportAdmin(admin.ModelAdmin):
    list_display = ('cleaner', 'service_request', 'description', 'completed_at', 'client_rating', 'forwarded')
    search_fields = ('cleaner', 'service_request')
admin.site.register(CleaningReport, CleaningReportAdmin)