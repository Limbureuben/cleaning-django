from django.urls import path # type: ignore
from .views import *

urlpatterns = [
    path('organizations-registration/', RegisterOrganizationView.as_view(), name='organizations-registration'),
    path('organizations-list/', OrganizationViewAdmin.as_view(), name='organizations-list'),
    path('organization/<int:pk>/update-status/', UpdateOrganizationStatusView.as_view(), name='update-organization-status'),
]
