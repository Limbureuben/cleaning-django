from django.urls import path # type: ignore
from .views import *

urlpatterns = [
    path('organizations-registration/', RegisterOrganizationView.as_view(), name='organizations-registration')
]
