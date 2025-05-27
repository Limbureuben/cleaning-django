from rest_framework import serializers
from .models import *


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        
class EmployeeSerializer(serializers.ModelSerializer):
    company=CompanySerializer(read_only=True)
    company_id=serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(),write_only=True,source="company")
    class Meta:
        model = Employee
        fields = ['employee_id', 'employee_name', 'employee_email', 'employee_phone', 'employee_role',
                  'is_active', 'created_at', 'updated_at', 'company', 'company_id']
        
class ServiceSerializer(serializers.ModelSerializer):
    company=CompanySerializer(read_only=True)
    company_id=serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(),write_only=True,source="company")
    class Meta:
        model=Service
        fields = ['service_id', 'name', 'hourly_rate', 'estimated_duration', 'description', 'company', 'company_id']
        

class BookingSerializer(serializers.ModelSerializer):
    company=CompanySerializer(read_only=True)
    company_id=serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(),write_only=True,source="company")
    customer=CustomerSerializer(read_only=True)
    customer_id=serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(),write_only=True,source="customer")
    service=ServiceSerializer(many=True,read_only=True)
    service_id=serializers.PrimaryKeyRelatedField(many=True,queryset=Service.objects.all(),write_only=True,source="service")
    
    class Meta:
        model = Booking
        fields = ['booking_id', 'customer', 'customer_id', 'company', 'company_id',
                  'service', 'service_id', 'date', 'time', 'hours_requested',
                  'total_price', 'status', 'created_at']
         
class ReviewSerializer(serializers.ModelSerializer):
    company=CompanySerializer(read_only=True)
    company_id=serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(),write_only=True,source="company")
    customer=CustomerSerializer(read_only=True)
    customer_id=serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(),write_only=True,source="customer")
    
    
    class Meta:
        model = Review
        fields = ['review_id', 'customer', 'customer_id', 'company', 'company_id',
                  'rating', 'comment', 'created_at']
