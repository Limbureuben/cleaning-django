from django.contrib import admin
from .models import *

# Register your models here.
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'location', 'email', 'address', 'services', 'user', 'status')
    search_fields = ('organization_name', 'location', 'email')
admin.site.register(Organization, OrganizationAdmin)

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'username', 'email', 'phone')
    search_fields = ('organization', 'username')
admin.site.register(ServiceRequest, ServiceRequestAdmin)