from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *

@api_view(['GET'])
def company_list(request):
    companies = Company.objects.filter(is_active=True)
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def company_detail(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    serializer = CompanySerializer(company)
    return Response(serializer.data)

@api_view(['POST'])
def create_company(request):
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    serializer = CompanySerializer(company, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    company.is_active=False
    company.save()
    return Response({"message":"Company Deleted Successful"},Status=status.HTTP_200_OK)  
