from rest_framework.exceptions import ValidationError
from rest_framework import serializers # type: ignore
from .models import *
from django.contrib.auth.password_validation import validate_password



# class RegisterCleanerSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)
#     passwordConfirm = serializers.CharField(write_only=True)
#     role = serializers.ChoiceField(choices=['is_cleaner'], default='is_cleaner')


class RegisterCleanerSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    passwordConfirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['is_cleaner'], default='is_cleaner')

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value


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
    organization_image = serializers.ImageField(source='organization.file', read_only=True)
    organization_location = serializers.CharField(source='organization.location', read_only=True)
    # organization_services = serializers.CharField(source='organization.services', read_only=True)
    status = serializers.CharField(read_only=True)  # include this to show status in the response

    # services_list = serializers.SerializerMethodField()

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
            'organization_location',
        ]

        # def get_services_list(self, obj):
        #     return obj.organization_services.split(', ') if obj.organization_services else []



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


class CleanerRequestSerializer(serializers.ModelSerializer):
    organization_location = serializers.CharField(source='organization.location', read_only=True)
    service_request_username = serializers.CharField(source='service_request.username', read_only=True)

    class Meta:
        model = CleanerRequest
        fields = ['id', 'username', 'email', 'cleaner_location', 'status', 'created_at', 'organization_location', 'service_request_username']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']



class CleaningReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningReport
        fields = '__all__'
        read_only_fields = ['cleaner']  # Prevent user from injecting wrong cleaner ID


class CleanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']