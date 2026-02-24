# patient/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    # Dashboard & Profile
    path('', views.dashboard, name='patient_dashboard'),
    path('updateprofile/', views.update_profile, name='update_profile'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.patient_login_view, name='login'),
    path('logout/', views.patient_logout_view, name='logout'),
    
    # Appointments
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('view_appointemnt/', views.view_appointment, name='view_appointemnt'),
    
    # Billing & Medical Records
    path('view_bills/', views.view_bills, name='view_bills'),
    path('pay-bill/<int:id>/', views.pay_bill, name='pay_bill'), 
    path('view_medical_history/', views.view_medical_history, name='view_medical_history'),
#   path('view_medical_request/', views.view_medical_request, name='view_medical_request'),
    path('paymentsuccess/<int:id>/', views.payment_success, name='payment_success'),
    # path('payment-cancel/<int:id>/', views.payment_cancel, name='payment_cancel'),
]