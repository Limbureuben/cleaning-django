from django.urls import path # type: ignore
from .views import *

urlpatterns = [
    path('organizations-registration/', RegisterOrganizationView.as_view(), name='organizations-registration'),
    path('organizations-list/', OrganizationViewAdmin.as_view(), name='organizations-list'),
    path('organization/<int:pk>/update-status/', UpdateOrganizationStatusView.as_view(), name='update-organization-status'),
    path('organization-status/', OrganizationStatusView.as_view(), name="Viewmyorganizationstatus"),
    path('fetch-approved/', FetchApprovedOrganization.as_view(), name="Approved-organizations"),
    path('user-profile/', UserProfileView.as_view(), name="user-profile"),
    path('send-service-request/', SendServiceRequest.as_view(), name="Request-services"),
    path('my-organization-requests/', StaffOrganizationRequests.as_view(), name='staff-organization-requests'),
    path('register-cleaner/', RegisterCleanersAPI.as_view(), name='register-cleaner'),
    path('available-cleaners/', AvailableCleanersView.as_view(), name='available-cleaners'),
]
