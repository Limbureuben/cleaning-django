from django.urls import path # type: ignore
from .views import *

urlpatterns = [
    path('api/v1/register/', UserRegistrationAPIView.as_view(), name='user-registration'),
]
