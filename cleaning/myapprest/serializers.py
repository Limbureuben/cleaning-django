from rest_framework import serializers
from .models import *

class RegisterOrganizationSerializer(serializers.ModelSerializer):
    # Make service a list field for input/output
    services = serializers.ListField(
        child=serializers.CharField(),
        write_only=True  # Will only be used during creation
    )
    service = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'user', 'organization_name', 'location', 'email', 'address', 'services', 'service']

    def create(self, validated_data):
        services = validated_data.pop('services', [])
        validated_data['service'] = ', '.join(services)  # Store as comma-separated string
        validated_data['user'] = self.context['request'].user  # Automatically set the user
        return super().create(validated_data)

    def get_service(self, obj):
        return obj.service.split(', ') if obj.service else []

