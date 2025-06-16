from django.contrib import admin
from .models import *

# Register your models here.
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('location', 'price', 'address', 'services', 'user', 'phone', 'status', 'guest', 'bedrooms', 'bathrooms', 'file')
    search_fields = ('location', 'price')
admin.site.register(Organization, OrganizationAdmin)

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'username', 'email', 'phone')
    search_fields = ('organization', 'username')
admin.site.register(ServiceRequest, ServiceRequestAdmin)



class CleanerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'location', 'contact', 'status')
    search_fields = ('location', 'full_name')
admin.site.register(Cleaner, CleanerAdmin)