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
        service_requests = ServiceRequest.objects.filter(status='available')
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




class CleanerRequestsFromCleanerAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        requests = CleanerRequest.objects.filter(from_user=request.user).order_by('-created_at')
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
            cleaner_request = CleanerRequest.objects.get(id=pk, from_user=request.user)
            if cleaner_request.status != 'cancelled':
                return Response({'detail': 'Only cancelled requests can be deleted.'}, status=status.HTTP_400_BAD_REQUEST)

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
            service_request.status = 'taken'
            service_request.save()

            return Response({'detail': 'Request approved and service marked as taken.'})

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
            cleaner_request.rejection_reason = reason  # Add this field to your model
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
