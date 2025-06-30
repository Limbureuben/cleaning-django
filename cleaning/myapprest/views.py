from django.shortcuts import render
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import *
from django.contrib.auth import authenticate
from rest_framework import status, permissions, authentication # type: ignore
from rest_framework.authtoken.models import Token # type: ignore
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view # type: ignore
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError



class RegisterCleanerAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RegisterCleanerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            if data['password'] != data['passwordConfirm']:
                return Response({'detail': 'Passwords must match.'}, status=status.HTTP_400_BAD_REQUEST)


            if CustomUser.objects.filter(username=data['username']).exists():
                return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = CustomUser(
                    username=data['username'],
                    email=data['email'],
                    role='is_cleaner',
                    registered_by=request.user
                )
                user.set_password(data['password'])
                user.save()
                return Response({'detail': 'Cleaner registered.'}, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response({'detail': 'A user with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class RegisterOrganizationView(APIView):
    # Only allow authenticated users to register organizations
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Create serializer without 'user' in request.data
        serializer = RegisterOrganizationSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            # Save and associate the logged-in user
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Print the errors for debugging
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        organizations = Organization.objects.all()
        serializer = RegisterOrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class OrganizationViewAdmin(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        organizations = Organization.objects.all()
        serializer = RegisterOrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UpdateOrganizationStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in dict(Organization.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        organization.status = new_status
        organization.save()
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FetchApprovedOrganization(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organizations = Organization.objects.filter(status="pending")
        serializer = FetchedOrganizationSerializer(organizations, many=True, context={'request': request})
        return Response(serializer.data)


class FetchToCleaner(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all service requests with status 'booked'
        service_requests = ServiceRequest.objects.filter(status='taken')
        serializer = ServiceRequestSerializer(service_requests, many=True, context={'request': request})
        return Response(serializer.data)


class SendServiceRequest(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = ServiceFromUserRequestSerializer(data=data)
        if serializer.is_valid():
            service_request = serializer.save(user=request.user)
            org = service_request.organization
            org.status = 'suspended'
            org.save()
            return Response({"success": "Request sent successfully"}, status=201)
        return Response(serializer.errors, status=400)




class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class StaffOrganizationRequests(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        # Get all organizations created by this staff user
        organizations = Organization.objects.filter(user=request.user)

        # Get service requests for those organizations
        requests = ServiceRequest.objects.filter(organization__in=organizations)

        serializer = ServiceRequestSerializer(requests, many=True)
        return Response(serializer.data)
    


class RegisterCleanersAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CleanerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailableCleanersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filter cleaners registered by the logged-in staff and who are available
        cleaners = Cleaner.objects.filter(user=request.user, status='available')
        serializer = CleanerSerializer(cleaners, many=True)
        return Response(serializer.data)
    


@api_view(['POST'])
def custom_login(request):
    # Authenticate user manually or use DRF's TokenObtainPairView
    user = authenticate(username=request.data['username'], password=request.data['password'])
    if not user:
        return Response({'error': 'Invalid credentials'}, status=401)

    # Create JWT tokens
    refresh = RefreshToken.for_user(user)

    # Determine role
    if user.is_superuser:
        role = 'admin'
    elif hasattr(user, 'cleaner_profile'):
        role = 'cleaner'
    elif user.is_staff:
        role = 'staff'
    else:
        role = 'user'

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username,
        'role': role
    })



class SubmitCleanerRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        service_request_id = request.data.get('service_request')
        username = request.data.get('username')
        email = request.data.get('email')
        location = request.data.get('cleaner_location')

        if not all([service_request_id, username, email, location]):
            return Response(
                {'detail': 'Missing required fields.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service_request = ServiceRequest.objects.get(id=service_request_id)
            organization = service_request.organization
            staff_user = organization.user
            client_user = service_request.user

            # Check if this cleaner has already sent a request for this service request
            exists = CleanerRequest.objects.filter(
                from_user=request.user,
                service_request=service_request
            ).exists()

            if exists:
                return Response(
                    {'detail': 'You have already sent a cleaning request for this booked house.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the cleaner request
            CleanerRequest.objects.create(
                from_user=request.user,
                to_user=staff_user,
                service_request=service_request,
                cleaner_location=location,
                username=username,
                email=email,
                status='pending'
            )

            # Send emails (you can keep your send_email helper as is)

            # ... (rest of your email code)

            return Response({'detail': 'Cleaner request submitted and notifications sent.'})

        except ServiceRequest.DoesNotExist:
            return Response({'detail': 'Service request not found.'}, status=status.HTTP_404_NOT_FOUND)



# class CleanerRequestsFromCleanerAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         requests = CleanerRequest.objects.filter(from_user=request.user).order_by('-created_at')
#         serializer = CleanerRequestSerializer(requests, many=True)
#         return Response(serializer.data)

class CleanerRequestsFromCleanerAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        requests = CleanerRequest.objects.filter(
            from_user=request.user
        ).exclude(
            status='approved'
        ).order_by('-created_at')

        serializer = CleanerRequestSerializer(requests, many=True)
        return Response(serializer.data)
    

class CleanerRequestsApprovedFromCleanerAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        requests = CleanerRequest.objects.filter(
            from_user=request.user,
            status='approved'  # Only approved
        ).order_by('-created_at')

        serializer = CleanerRequestSerializer(requests, many=True)
        return Response(serializer.data)



class CleanerRequestsToStaffAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        requests = CleanerRequest.objects.filter(to_user=request.user).order_by('-created_at')
        serializer = CleanerRequestSerializer(requests, many=True)
        return Response(serializer.data)
    


class CancelCleanerRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, request_id):
        try:
            cleaner_request = CleanerRequest.objects.get(id=request_id, from_user=request.user)

            if cleaner_request.status != 'pending':
                return Response({'detail': 'Only pending requests can be cancelled.'}, status=400)

            # Mark as cancelled
            cleaner_request.status = 'cancelled'
            cleaner_request.save()

            # Optionally revert the ServiceRequest to 'available'
            service_request = cleaner_request.service_request
            service_request.status = 'available'
            service_request.save()

            return Response({'detail': 'Cleaner request cancelled successfully.'})

        except CleanerRequest.DoesNotExist:
            return Response({'detail': 'Request not found or not owned by you.'}, status=404)



class DeleteCleanerRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            cleaner_request = CleanerRequest.objects.get(id=pk)

            # Check if current user is the receiving staff
            if cleaner_request.to_user != request.user:
                return Response({'detail': 'You are not allowed to delete this request.'}, status=status.HTTP_403_FORBIDDEN)

            if cleaner_request.status not in ['approved', 'cancelled']:
                return Response({'detail': 'Only approved or cancelled requests can be deleted.'}, status=status.HTTP_400_BAD_REQUEST)

            cleaner_request.delete()
            return Response({'detail': 'Request deleted successfully.'}, status=status.HTTP_200_OK)

        except CleanerRequest.DoesNotExist:
            return Response({'detail': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)




class CleanerDeleteRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            cleaner_request = CleanerRequest.objects.get(id=pk, from_user=request.user)
            if cleaner_request.status != 'approved':
                return Response({'detail': 'Only approved requests can be deleted.'}, status=status.HTTP_400_BAD_REQUEST)


            cleaner_request.delete()
            return Response({'detail': 'Request deleted successfully.'}, status=status.HTTP_200_OK)

        except CleanerRequest.DoesNotExist:
            return Response({'detail': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)



class ApproveCleanerRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            cleaner_request = CleanerRequest.objects.get(id=pk)

            if cleaner_request.status != 'pending':
                return Response({'detail': 'Only pending requests can be approved.'}, status=400)

            # Approve the request
            cleaner_request.status = 'approved'
            cleaner_request.save()

            # Mark the service request as taken
            service_request = cleaner_request.service_request
            service_request.status = 'approved'
            service_request.save()

            cleaner = cleaner_request.from_user
            client = service_request.user

            create_notification(
                user=cleaner,
                title="Cleaning Request Approved",
                message=f"Hi {cleaner.username}, your request to clean the house booked by {service_request.username} has been approved."
            )

            create_notification(
                user=client,
                title="Cleaner Assigned",
                message=f"A cleaner ({cleaner.username}) has been assigned to clean your booked house."
            )

            # Send email to client with cleaner details
            client_email = client.email
            subject_client = "Cleaner Assigned for Your Booked House"

            message_client = f"""
            Hello {client.username},

            We are happy to inform you that a cleaner has been assigned to clean the house you booked.

            Cleaner Details:
            -----------------------------
            Name: {cleaner.username}
            Location: {cleaner_request.cleaner_location}
            ✉️ Email: {cleaner.email}
            📅 Start Date: {service_request.start_date}
            📅 End Date: {service_request.end_date}

            Status: Approved and scheduled for cleaning.

            If you have any questions, feel free to reply to this email.

            Thank you for using our service.

            Sincerely,
            Open Space Cleaning Team
            """

            send_mail(
                subject=subject_client,
                message=message_client,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client_email],
                fail_silently=False,
            )

            # Send email to cleaner
            subject_cleaner = "Your Cleaning Request Approved"
            message_cleaner = f"Hi {cleaner.username}, your cleaning request has been approved by the staff."

            send_mail(
                subject=subject_cleaner,
                message=message_cleaner,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cleaner.email],
                fail_silently=False,
            )

            return Response({'detail': 'Request approved, service marked as taken, notifications sent.'})

        except CleanerRequest.DoesNotExist:
            return Response({'detail': 'Cleaner request not found.'}, status=404)





class CleanerRequestRejectAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        reason = request.data.get('reason')
        if not reason:
            return Response({'detail': 'Rejection reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cleaner_request = CleanerRequest.objects.get(pk=pk)
            cleaner_request.status = 'rejected'
            cleaner_request.rejection_reason = reason
            cleaner_request.save()

            # Send rejection email to cleaner
            send_mail(
                subject='Cleaning Request Rejected',
                message=f"Your cleaning request was rejected for the following reason:\n\n{reason}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cleaner_request.email],
                fail_silently=False,
            )

            return Response({'detail': 'Request rejected and cleaner notified.'})

        except CleanerRequest.DoesNotExist:
            return Response({'detail': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)


def create_notification(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)


class NotificationListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'detail': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found.'}, status=404)
        

class UnreadNotificationCountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})



class DeleteNotificationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.delete()
            return Response({"detail": "Notification deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)



# class SubmitCleanerRatingAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         cleaner_id = request.data.get('cleaner_id')
#         service_id = request.data.get('service_request_id')
#         rating = request.data.get('rating')
#         comment = request.data.get('comment', '')

#         if not all([cleaner_id, service_id, rating]):
#             return Response({'detail': 'Missing data'}, status=400)

#         cleaner = User.objects.get(id=cleaner_id)
#         service = ServiceRequest.objects.get(id=service_id)

#         CleanerRating.objects.create(
#             cleaner=cleaner,
#             client=request.user,
#             service_request=service,
#             rating=rating,
#             comment=comment
#         )

#         return Response({'detail': 'Rating submitted successfully'})




class CleaningReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Staff sees all reports, others see only related reports
        if user.is_staff:
            reports = CleaningReport.objects.all()
        else:
            reports = CleaningReport.objects.filter(
                models.Q(cleaner=user) | models.Q(service_request__booked_by=user)
            )
        serializer = CleaningReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['cleaner'] = request.user.id  # Add this line to ensure cleaner is included
        serializer = CleaningReportSerializer(data=data)

        if serializer.is_valid():
            serializer.save(cleaner=request.user)  # Pass the cleaner explicitly
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StaffCleanersAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        staff_user = request.user

        if staff_user.role != 'staff':
            return Response({'error': 'Only staff can view registered cleaners.'}, status=403)

        # Get users with role 'is_cleaner' registered by this staff
        cleaners = CustomUser.objects.filter(role='is_cleaner', registered_by=staff_user)

        serializer = CleanerSerializer(cleaners, many=True)

        return Response({
            'total_cleaners': cleaners.count(),
            'cleaners': serializer.data
        })




class CleanerReportRatingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            report = CleaningReport.objects.get(pk=pk)
        except CleaningReport.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != report.service_request.booked_by:
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        rating = request.data.get('client_rating')
        if not rating or not (1 <= int(rating) <= 5):
            return Response({'detail': 'Invalid rating (1-5)'}, status=status.HTTP_400_BAD_REQUEST)

        report.client_rating = int(rating)
        report.save()
        return Response({'detail': 'Rating saved successfully'})


class StaffDashboardStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        staff_user = request.user

        # Get organizations registered by this staff
        staff_organizations = Organization.objects.filter(user=staff_user)
        total_organizations = staff_organizations.count()

        # Get service requests for those organizations
        total_service_requests = ServiceRequest.objects.filter(
            organization__in=staff_organizations
        ).count()

        return Response({
            "total_organizations": total_organizations,
            "total_service_requests": total_service_requests
        })




class ServiceRequestActionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            service_request = ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=404)

        user = service_request.user
        org = service_request.organization
        address = org.address
        location = org.location

        action = request.data.get('action')

        if action == 'accept':
            service_request.status = 'taken'
            service_request.save()

            # Send email
            send_mail(
                subject="Request Accepted",
                message=f"Your request for the house at {address}, located in {location}, has been accepted.",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True
            )

            # Save Notification
            Notification.objects.create(
                user=user,
                title="Request Accepted",
                message=f"Your request for the house at {address}, located in {location}, has been accepted."
            )

            return Response({'success': 'Request accepted and notification sent'})

        elif action == 'reject':
            service_request.status = 'rejected'
            service_request.save()

            send_mail(
                subject="Request Rejected",
                message=f"Your request for the house at {address}, located in {location}, has been rejected.",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True
            )

            Notification.objects.create(
                user=user,
                title="Request Rejected",
                message=f"Your request for the house at {address}, located in {location}, has been rejected."
            )

            return Response({'success': 'Request rejected and notification sent'})

        elif action == 'delete':
            if service_request.status in ['taken', 'rejected']:
                service_request.delete()
                return Response({'success': 'Request deleted'})
            return Response({'error': 'Cannot delete a request unless it is accepted or rejected'}, status=400)

        else:
            return Response({'error': 'Invalid action'}, status=400)




class CleanerReportRatingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            report = CleaningReport.objects.get(pk=pk)
        except CleaningReport.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        service_request = report.service_request

        # Only client who booked the service can rate
        if request.user != service_request.user:
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        # Prevent double rating for this specific request
        if CleanerRating.objects.filter(service_request=service_request).exists():
            return Response({'detail': 'You have already rated this service'}, status=status.HTTP_400_BAD_REQUEST)

        rating = request.data.get('rating')

        if not rating or not (1 <= int(rating) <= 5):
            return Response({'detail': 'Invalid rating (1-5)'}, status=status.HTTP_400_BAD_REQUEST)

        # Save rating
        CleanerRating.objects.create(
            cleaner=report.cleaner,
            client=request.user,
            service_request=service_request,
            rating=int(rating),
        )

        return Response({'detail': 'Rating submitted successfully'})




class StaffCleaningReportsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'staff':
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        reports = CleaningReport.objects.filter(
            service_request__organization__user=request.user
        ).select_related('cleaner', 'service_request', 'service_request__user')  # prefetch user (the client)

        data = [
            {
                'id': report.id,
                'cleaner': report.cleaner.username,
                'client': report.service_request.user.username,  # fixed here
                'description': report.description,
                'completed_at': report.completed_at,
                'attachment': report.attachment.url if report.attachment else None,
                'client_rating': report.client_rating,
                'forwarded': report.forwarded,  # Add this line in your `data` list
            }
            for report in reports
        ]
        return Response(data)
    
    def delete(self, request, pk):
        try:
            report = CleaningReport.objects.get(pk=pk)
        except CleaningReport.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=404)

        if not report.forwarded:
            return Response({'detail': 'Cannot delete before forwarding'}, status=400)

        report.delete()
        return Response({'detail': 'Report deleted'})


class ForwardReportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            report = CleaningReport.objects.get(pk=pk)
        except CleaningReport.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=404)

        report.forwarded = True
        report.save()
        # Optionally: Notify client here
        return Response({'detail': 'Report forwarded'})


class ClientForwardedReportsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'user':
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        reports = CleaningReport.objects.filter(
            forwarded=True,
            service_request__user=request.user
        ).select_related('cleaner', 'service_request')

        data = [
            {
                'id': report.id,
                'cleaner': report.cleaner.username,
                'description': report.description,
                'completed_at': report.completed_at,
                'attachment': report.attachment.url if report.attachment else None,
                'client_rating': report.client_rating,
            }
            for report in reports
        ]

        return Response(data, status=200)


class CleanerDashboardStatsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. Available Jobs (status='taken')
        available_jobs = ServiceRequest.objects.filter(status='taken')
        available_jobs_count = available_jobs.count()

        # 2. Total Cleaner Requests (excluding approved)
        total_cleaner_requests = CleanerRequest.objects.filter(from_user=user).exclude(status='approved')
        total_cleaner_requests_count = total_cleaner_requests.count()

        # 3. Total Approved Cleaner Requests
        approved_requests = CleanerRequest.objects.filter(from_user=user, status='approved')
        approved_requests_count = approved_requests.count()

        return Response({
            "available_jobs_count": available_jobs_count,
            "total_cleaner_requests_count": total_cleaner_requests_count,
            "approved_cleaner_requests_count": approved_requests_count
        })