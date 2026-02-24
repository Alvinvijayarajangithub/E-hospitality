from django.contrib import admin
# Use 'include' for app urls and 'path' for routing
from django.urls import path, include
from django.shortcuts import redirect 

# Importing views from your apps
from patient import views as patient_views
from adminpanel import views as admin_views

# project/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),

    # Change the root redirect to point specifically to the patient login
    path('', lambda request: redirect('patient_login'), name='root_redirect'),

    # Give these unique names
    path('login/', patient_views.patient_login_view, name='patient_login'),
    path('logout/', patient_views.patient_logout_view, name='patient_logout'),
    
    # App inclusions
    path('patient/', include('patient.urls')),
    path('doctor/', include('doctor.urls')), 
    path('adminpanel/', include('adminpanel.urls')),
]