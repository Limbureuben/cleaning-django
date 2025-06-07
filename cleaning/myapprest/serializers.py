from rest_framework import serializers # type: ignore
from .models import *

class RegisterOrganizationSerializer(serializers.ModelSerializer):
    # Use a list field for input
    services = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )
    # Return a list of services as read-only
    services_list = serializers.SerializerMethodField(read_only=True)

    # Make the user field read-only
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'user', 'organization_name', 'location', 'email', 'address', 'services', 'services_list', 'status']

    def create(self, validated_data):
        # Get the list of services
        services_list = validated_data.pop('services', [])
        # Store as comma-separated string
        validated_data['services'] = ', '.join(services_list)
        # Set the user automatically
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
    class Meta:
        model = Organization
        fields = ['id', 'organization_name', 'location', 'email', 'address', 'services']


class ServiceRequestSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.organization_name', read_only=True)
    class Meta:
        model = ServiceRequest
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']



class CleanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cleaner
        fields = '__all__'