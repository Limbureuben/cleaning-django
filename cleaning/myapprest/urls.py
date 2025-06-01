from django.urls import path # type: ignore
from .views import *

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='login'),
]
