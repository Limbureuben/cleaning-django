from django.urls import path # type: ignore
from .views import *

urlpatterns = [
    path('organizations-registration/', RegisterOrganizationView.as_view(), name='organizations-registration'),
    path('organizations-list/', OrganizationViewAdmin.as_view(), name='organizations-list'),
    path('organization/<int:pk>/update-status/', UpdateOrganizationStatusView.as_view(), name='update-organization-status'),
    path('fetch-approved/', FetchApprovedOrganization.as_view(), name="Approved-organizations"),
    path('fetch-to-cleaner/', FetchToCleaner.as_view(), name="Fetch-organization-to-cleaner"),
    path('user-profile/', UserProfileView.as_view(), name="user-profile"),
    path('send-service-request/', SendServiceRequest.as_view(), name="Request-services"),
    path('my-organization-requests/', StaffOrganizationRequests.as_view(), name='staff-organization-requests'),
    path('register-cleaner/', RegisterCleanersAPI.as_view(), name='register-cleaner'),
    path('available-cleaners/', AvailableCleanersView.as_view(), name='available-cleaners'),
    path('client-send-service-request/', SubmitCleanerRequestAPIView.as_view(), name='submit-cleaner-request'),
    path('cleaner-requests/from-cleaner/', CleanerRequestsFromCleanerAPIView.as_view()),
    path('cleaner-requests/to-staff/', CleanerRequestsToStaffAPIView.as_view(), name='cleaner-requests-to-staff'),
    path('cancel-cleaner-request/<int:request_id>/', CancelCleanerRequestAPIView.as_view(), name='cancel-cleaner-request'),
    path('delete-cleaner-request/<int:pk>/', DeleteCleanerRequestAPIView.as_view(), name='delete-cleaner-request'),
    path('cleaner-requests/<int:pk>/approve/', ApproveCleanerRequestAPIView.as_view(), name='approve-cleaner-request'),
    path('cleaner-requests/<int:pk>/reject/', CleanerRequestRejectAPIView.as_view(), name='reject-cleaner-request'),
    path('api/notifications/', NotificationListAPIView.as_view(), name='notifications'),
    path('api/notifications/<int:pk>/mark-read/', MarkNotificationAsReadAPIView.as_view(), name='mark-notification-read'),
    path('api/notifications/unread-count/', UnreadNotificationCountAPIView.as_view(), name='unread-notification-count'),
]