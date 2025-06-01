# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('staff', 'Staff'), ('user', 'User')], required=False)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role = validated_data.pop('role', 'user')  # Default to 'user' if not provided

        user = User(**validated_data)
        user.is_staff = True if role == 'staff' else False
        user.set_password(validated_data['password'])
        user.save()
        return user
