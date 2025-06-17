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


class OrganizationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['organization_name', 'location', 'email',  'status']

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


class ServiceRequestSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.organization_name', read_only=True)
    class Meta:
        model = ServiceRequest
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']



# serializers.py
class CleanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cleaner
        fields = ['id', 'full_name', 'location', 'contact', 'status', 'user']
        read_only_fields = ['user', 'status']
