# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(default=False, required=False)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        is_staff = validated_data.pop('is_staff', False)
        user = User(**validated_data)
        user.is_staff = is_staff  # Default to False if not provided
        user.set_password(validated_data['password'])
        user.save()
        return user
