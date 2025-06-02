from django.contrib import admin
from .models import *

# Register your models here.
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'location', 'email', 'address', 'service')
    search_fields = ('organization_name', 'location', 'email')
admin.site.register(Organization, OrganizationAdmin)