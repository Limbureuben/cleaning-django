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


class OrganizationStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        # Get organizations for the current logged-in user
        organizations = Organization.objects.filter(user=request.user)
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)

class FetchApprovedOrganization(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        organization = Organization.objects.filter(status="approved")
        serializer = FetchedOrganizationSerializer(organization, many=True)
        return Response(serializer.data)


class SendServiceRequest(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = ServiceRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
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
        serializer = CleanerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

