from rest_framework.exceptions import ValidationError
from rest_framework import serializers # type: ignore
from .models import *

class RegisterOrganizationSerializer(serializers.ModelSerializer):
    services = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )
    services_list = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'user', 'location', 'price', 'address',
            'phone', 'file', 'services', 'services_list', 'guests', 'bedrooms', 'bathrooms', 'status'
        ]


    def create(self, validated_data):
        services_list = validated_data.pop('services', [])
        validated_data['services'] = ', '.join(services_list)
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def get_services_list(self, obj):
        return obj.services.split(', ') if obj.services else []


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


# class OrganizationStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Organization
#         fields = ['organization_name', 'location', 'email',  'status']

class FetchedOrganizationSerializer(serializers.ModelSerializer):
    services_list = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()  # Ensures full file URL

    class Meta:
        model = Organization
        fields = ['id', 'location', 'price', 'bedrooms', 'guests', 'bathrooms', 'address', 'phone', 'file', 'services', 'services_list']

    def get_services_list(self, obj):
        return obj.services.split(', ') if obj.services else []

    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None



# serializers.py

class ServiceRequestSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_image = serializers.ImageField(source='organization.image', read_only=True)
    organization_location = serializers.CharField(source='organization.location', read_only=True)
    status = serializers.CharField(read_only=True)  # include this to show status in the response

    class Meta:
        model = ServiceRequest
        fields = [
            'id',
            'user',
            'username',
            'email',
            'phone',
            'start_date',
            'end_date',
            'requested_at',
            'status',
            'organization_name',
            'organization_image',
            'organization_location'
        ]


class ServiceFromUserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = '__all__'



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']



# serializers.py
class CleanerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Cleaner
        fields = ['id', 'full_name', 'location', 'contact', 'status', 'username', 'email', 'password']
        read_only_fields = ['status']

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        registered_by = self.context['request'].user

        # ✅ Check for unique username
        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'This username is already taken.'})

        auth_user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )


        cleaner = Cleaner.objects.create(
            auth_user=auth_user,
            registered_by=registered_by,
            **validated_data
        )
        return cleaner