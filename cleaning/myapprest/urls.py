from django.urls import path
from . import views

urlpatterns = [
    # This endpoint url pointd for company CRUD operations 
    path('companies/', views.company_list, name='company-list'),
    path('companies/<uuid:company_id>/', views.company_detail, name='company-detail'),
    path('companies/create/', views.create_company, name='company-create'),
    path('companies/<uuid:company_id>/update/', views.update_company, name='company-update'),
    path('companies/<uuid:company_id>/delete/', views.delete_company, name='company-delete'),
    path('companies/<uuid:company_id>/reviews/', views.company_reviews, name='company-reviews'),
    # This endpoint url pointd for review CRUD operations
    path('reviews/', views.review_list, name='review-list'), 
    path('reviews/<uuid:review_id>/', views.review_detail, name='review-detail'),
    path('reviews/create/', views.create_review, name='review-create'),
    path('reviews/<uuid:review_id>/update/', views.update_review, name='review-update'),
    path('reviews/<uuid:review_id>/delete/', views.delete_review, name='review-delete'),
    # This endpoint url pointd for employee CRUD operations
    path('employees/', views.employee_list, name='employee-list'),
    path('employees/<uuid:employee_id>/', views.employee_detail, name='employee-detail'),
    path('employees/create/', views.create_employee, name='employee-create'),
    path('employees/<uuid:employee_id>/update/', views.update_employee, name='employee-update'),
    path('employees/<uuid:employee_id>/delete/', views.delete_employee, name='employee-delete'),
   

]
