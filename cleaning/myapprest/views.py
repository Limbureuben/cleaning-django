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



# class SubmitCleanerRequestAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         print("📥 Incoming cleaner request:", request.data)

#         service_request_id = request.data.get('service_request')  # the house the cleaner wants to clean
#         username = request.data.get('username')
#         email = request.data.get('email')
#         location = request.data.get('cleaner_location')

#         if not all([service_request_id, username, email, location]):
#             return Response(
#                 {'detail': 'Missing required fields.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             service_request = ServiceRequest.objects.get(id=service_request_id)
#             organization = service_request.organization
#             staff_user = organization.user  # assumes Organization has a .user (staff) field

#             # Save cleaner request
#             CleanerRequest.objects.create(
#                 from_user=request.user,
#                 to_user=staff_user,
#                 service_request=service_request,
#                 cleaner_location=location,
#                 username=username,
#                 email=email,
#                 status='pending'
#             )

#             # Email notification to cleaner
#             send_mail(
#                 subject='Cleaning Request Submitted',
#                 message=f"Hi {username},\n\nYour request to clean the house booked by {service_request.username} has been submitted.",
#                 from_email='noreply@example.com',
#                 recipient_list=[email],
#                 fail_silently=False,
#             )

#             return Response({'detail': 'Cleaner request submitted successfully.'})

#         except ServiceRequest.DoesNotExist:
#             return Response({'detail': 'Service request not found.'}, status=status.HTTP_404_NOT_FOUND)



class SubmitCleanerRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("📥 Incoming cleaner request:", request.data)

        service_request_id = request.data.get('service_request')  # booked house ID
        username = request.data.get('username')
        email = request.data.get('email')  # cleaner email
        location = request.data.get('cleaner_location')

        if not all([service_request_id, username, email, location]):
            return Response(
                {'detail': 'Missing required fields.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service_request = ServiceRequest.objects.get(id=service_request_id)
            organization = service_request.organization
            staff_user = organization.user  # staff user
            client_user = service_request.user  # client who booked the house

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

            # Update the service request status to 'taken'
            service_request.status = 'taken'
            service_request.save()

            # Email sending helper function with basic error handling
            def send_email(subject, message, recipient):
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient],
                        fail_silently=False,
                    )
                except BadHeaderError:
                    print(f"Invalid header found when sending email to {recipient}")
                except Exception as e:
                    print(f"Error sending email to {recipient}: {e}")

            # Send emails
            send_email(
                subject='Cleaning Request Submitted',
                message=f"Hi {username},\n\nYour cleaning request for the house booked by {service_request.username} has been submitted.",
                recipient=email
            )

            send_email(
                subject='New Cleaning Request',
                message=f"Hello {staff_user.username},\n\nA new cleaning request has been submitted by {username} for the house booked by {service_request.username}.",
                recipient=staff_user.email
            )

            send_email(
                subject='Your House Cleaning Requested',
                message=f"Dear {service_request.username},\n\nA cleaner ({username}) has requested to clean your booked house at {location}.",
                recipient=client_user.email
            )

            return Response({'detail': 'Cleaner request submitted and notifications sent.'})

        except ServiceRequest.DoesNotExist:
            return Response({'detail': 'Service request not found.'}, status=status.HTTP_404_NOT_FOUND)
