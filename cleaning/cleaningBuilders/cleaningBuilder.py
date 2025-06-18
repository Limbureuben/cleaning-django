from django.forms import ValidationError
from myapp.models import *
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from cleaning_dto.Response import *
from cleaning_dto.cleaning import *


class UserBuilder:
    @staticmethod
    def register_user(username, password, passwordConfirm, role='user', email=''):
        if password != passwordConfirm:
            raise ValidationError("Passwords do not match")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Username already taken")

        if role not in ['user', 'staff', 'cleaner']:
            raise ValidationError("Invalid role")
        
        if email:
            try:
                validate_email(email)
            except DjangoValidationError:
                raise ValidationError("Invalid email format")
            
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Email already taken")

        user = CustomUser(username=username, role=role, email=email)
        user.set_password(password)
        user.is_superuser = False
        user.is_staff = role == 'staff'
        user.save()
        return user

def register_user(input):
    try:
        role = getattr(input, 'role', 'user') or 'user'
        ward = getattr(input, 'cleaner', None)
        user = UserBuilder.register_user(input.username, input.password, input.passwordConfirm, role=role, email=getattr(input, 'email', ''), ward=ward)
        
        return RegistrationResponse(
            message="User registration successful",
            success=True,
            user=RegistrationObject(id=str(user.id), username=user.username)
        )
    except ValidationError as e:
        return RegistrationResponse(message=str(e), success=False, user=None)
