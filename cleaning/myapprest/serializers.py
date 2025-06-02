# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *


class RegisterOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'