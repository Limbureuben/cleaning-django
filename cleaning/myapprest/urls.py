from django.urls import path
from . import views

urlpatterns = [
    # This endpoint url pointd for company CRUD operations 
    path('companies/', views.company_list, name='company-list'),
    path('companies/<uuid:company_id>/', views.company_detail, name='company-detail'),
    path('companies/create/', views.create_company, name='company-create'),
    path('companies/<uuid:company_id>/update/', views.update_company, name='company-update'),
    path('companies/<uuid:company_id>/delete/', views.delete_company, name='company-delete'),

]
