# adminpanel/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('login/', views.login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('generate-bill/<int:id>/', views.generate_bill, name='generate_bill'),
    
    #appoinment 
    path('appoinment-request/', views.appoinment_request, name='appoinment_request'),
    path('appointment-history/', views.appointment_history, name='appoinment_history'),
    path('approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    
    #patient
    path('patient-list/', views.patient_list, name='patient_list'),
    path('patients/delete/<int:id>/', views.patient_delete, name='patient_delete'),
    path('patient-statistics/', views.patient_statistics, name='patient_statistics'),
    
    
    path('billing-dashboard/', views.billing_dashboard, name='billing_dashboard'),
    
    #doctor
    path('doctor-list/', views.doctor_list, name='doctor_list'),
     path('doctor-delete/<int:id>/', views.doctor_delete, name='doctor_delete'),
    
]