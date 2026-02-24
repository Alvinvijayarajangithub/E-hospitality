from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('login/', views.doctor_login_view, name='doctor_login'),
    path('logout/', views.doctor_logout_view, name='doctor_logout'),
    # path('my-appointments/', views.doctor_appointments_list, name='doctor_appointments'), # This now exists!
    path('complete/<int:id>/', views.complete_appointment, name='complete_appointment'),
    path('reject/<int:id>/', views.reject_appointment, name='reject_doctor_appointment'),
    path('register/', views.doctor_register_view, name='doctor_register'),
    path('complete-consultation/<int:appointment_id>/', views.complete_consultation, name='complete_consultation'),
]