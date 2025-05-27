from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'company_name', 'region_located', 'location', 'price',
        'discount', 'rating', 'available_date', 'is_available', 'is_active'
    )
    list_filter = ('region_located', 'is_available', 'is_active', 'available_date')
    search_fields = ('company_name', 'location', 'region_located')
    list_per_page = 10
    ordering = ('-created_at',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_name', 'employee_email', 'employee_phone', 'employee_role', 'company', 'is_active')
    list_filter = ('employee_role', 'is_active', 'company')
    search_fields = ('employee_name', 'employee_email', 'company__company_name')
    list_per_page = 10
    ordering = ('-created_at',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'hourly_rate', 'estimated_duration')
    search_fields = ('name', 'company__company_name')
    list_filter = ('company',)
    ordering = ('name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'customer_phonenumber', 'is_active')
    search_fields = ('customer_name', 'customer_email', 'customer_phonenumber')
    list_filter = ('is_active',)
    ordering = ('-created_at',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'company', 'date', 'time', 'status', 'total_price')
    list_filter = ('status', 'date', 'company')
    search_fields = ('customer__customer_name', 'company__company_name')
    ordering = ('-created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'company', 'rating', 'created_at')
    search_fields = ('customer__customer_name', 'company__company_name')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)

