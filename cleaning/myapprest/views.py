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
        return Response({"message":"Company created Successfull","data":serializer.data},status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    serializer = CompanySerializer(company, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Company Updated Successfully","data":serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_company(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    company.is_active=False
    company.save()
    serializer = CompanySerializer(company)
    return Response({"message":"Company Deleted Successful","data":serializer.data},status=status.HTTP_200_OK)  

@api_view(['GET'])
def review_list(request):
    reviews = Review.objects.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def company_reviews(request, company_id):
    reviews = Review.objects.filter(company__id=company_id)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['POST'])
def create_review(request):
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"You Submitted review succesfull","data":serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    serializer = ReviewSerializer(review, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Review updated_succesfull","data":serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    review.is_active=False
    review.save()
    serializer = ReviewSerializer(review)
    return Response({"message": "Review deleted successfully.","data":serializer.data}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def employee_list(request):
    employees = Employee.objects.filter(is_active=True)
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    serializer = EmployeeSerializer(employee)
    return Response(serializer.data)

@api_view(['POST'])
def create_employee(request):
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Employee created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Review updated_succesfull","data":serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    employee.is_active = False  
    employee.save()
    serializer = EmployeeSerializer(employee)
    return Response({
        "message": "Employee deleted successfully.",
        "data": serializer.data
    }, status=status.HTTP_200_OK)