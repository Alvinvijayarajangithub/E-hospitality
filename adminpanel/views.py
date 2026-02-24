from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from patient.models import Appointment
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from doctor.models import DoctorProfile
from django.shortcuts import render, redirect
from patient.models import PatientProfile
from django.db.models import Count
import calendar
from datetime import datetime
from django.db.models import Sum
from django.db.models.functions import TruncMonth

# Helper to check if user is admin
def is_admin(user):
    return user.is_superuser


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def appoinment_request(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        doctor_user_id = request.POST.get('doctor') # Get the doctor ID from the <select>

        appointment = get_object_or_404(Appointment, id=appointment_id)

        if action == 'approve':
            if doctor_user_id:
                # 1. Fetch the actual User object for the doctor
                doctor_user = get_object_or_404(User, id=doctor_user_id)
                # 2. Assign the doctor to the appointment
                appointment.doctor = doctor_user
                appointment.status = 'Approved'
                appointment.save()
                messages.success(request, f"Appointment for {appointment.patient.username} approved and assigned to Dr. {doctor_user.username}.")
            else:
                messages.error(request, "Please select a doctor before approving.")
                return redirect('appoinment_request')
        
        elif action == 'reject':
            appointment.status = 'Rejected'
            appointment.save()
            messages.info(request, "Appointment has been rejected.")

        return redirect('appoinment_request')

    # Fetching logic remains the same
    appointments = Appointment.objects.filter(status='Pending').order_by('-created_at')
    doctors = DoctorProfile.objects.all().select_related('user')

    return render(request, 'appoinment_request.html', {
        'appointments': appointments,
        'doctors': doctors
    })
    
@login_required
def admin_dashboard(request):
    return render(request,'admindashboard.html')
    
     
    
@login_required
@user_passes_test(is_admin)
def manage_appointments(request):
    # Consistency fix: changed 'PENDING' to 'Pending'
    appointments = Appointment.objects.filter(status='Pending')
    doctors = User.objects.filter(groups__name='Doctor')

    return render(request, 'admin/manage_appointments.html', {
        'appointments': appointments,
        'doctors': doctors
    })
    
@login_required
@user_passes_test(is_admin)
def approve_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)

    if request.method == "POST":
        doctor_id = request.POST.get('doctor')  # The ID from the <select> dropdown
        
        if doctor_id:
            # FIX: Fetch the actual User object using the ID
            doctor_user = get_object_or_404(User, id=doctor_id)
            
            # Assign the User object to the ForeignKey field
            appointment.doctor = doctor_user 
            appointment.status = 'Approved'
            appointment.save()
            
            messages.success(request, f"Appointment assigned to {doctor_user.username}")
            return redirect('appoinment_request')
        else:
            messages.error(request, "Please select a doctor.")

    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def generate_bill(request, id):
    appointment = get_object_or_404(Appointment, id=id)

    if request.method == "POST":
        amount = request.POST.get('amount')
        if amount:
            appointment.bill_amount = amount
            # Optionally change status to Completed when billing
            appointment.status = 'Completed' 
            appointment.save()
            messages.success(request, f"Bill generated for {appointment.patient.username}.")
            return redirect('admin_dashboard')

    return render(request, 'generate_bill.html', {'appointment': appointment})




# This handles the login SPECIFICALLY for the admin style


def login_view(request):
    # 1. Handle the Form Submission (POST)
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Authenticate against the database
        user = authenticate(request, username=u, password=p)
        
        # Check if user exists and has admin privileges
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            # Provide feedback if login fails
            messages.error(request, "Invalid Admin Credentials")
            return redirect('admin_login')
    
    # 2. Handle the Page Load (GET)
    # This is the "FIX" that prevents the 'Returned None' error
    return render(request, 'loginadmin.html')

def admin_logout_view(request):
    logout(request)
    # This sends the admin back to the Admin Login page specifically
    return redirect('admin_login')

@login_required
def appointment_history(request):
    appointments = Appointment.objects.exclude(status='Pending').order_by('-created_at')
    return render(request, 'appoinment._history.html', {
        'appointments': appointments
    })

@login_required
@user_passes_test(is_admin)
def patient_list(request):
    from patient.models import PatientProfile

    patients = PatientProfile.objects.select_related('user')

    return render(request, 'patient_list.html', {
        'patients': patients
    })

@login_required
def patient_statistics(request):
    return render(request,'patient_statistics.html')

@login_required
@user_passes_test(is_admin)
def billing_dashboard(request):
    # 1. Fetch full objects so we can use dot notation in templates
    # select_related('patient') makes it faster by joining the User table
    appointments_list = Appointment.objects.all().select_related('patient').order_by('-created_at')

    # 2. Total revenue
    total_revenue = Appointment.objects.filter(status='Completed').aggregate(total=Sum('bill_amount'))['total'] or 0

    # 3. Monthly revenue chart (Keep .values here as it's better for grouping)
    monthly_data = (
        Appointment.objects.filter(status='Completed')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('bill_amount'))
        .order_by('month')
    )

    labels = [calendar.month_name[dt['month'].month] + f" {dt['month'].year}" for dt in monthly_data]
    data = [float(dt['total']) for dt in monthly_data]

    context = {
        'appointments': appointments_list, # Passing the full objects
        'total_revenue': total_revenue,
        'chart_labels': labels,
        'chart_data': data,
    }
    return render(request, 'billing_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def doctor_list(request):
    # Fetch all doctors with their profile info
    doctors = DoctorProfile.objects.select_related('user').all()
    
    return render(request, 'doctor_list.html', {'doctors': doctors})

@login_required
@user_passes_test(is_admin)
def doctor_delete(request, id):
    doctor = get_object_or_404(DoctorProfile, id=id)
    
    # Delete linked user → automatically deletes profile (CASCADE)
    user = doctor.user
    user.delete()
    
    messages.success(request, f"Doctor {doctor.user.username} deleted successfully.")
    return redirect('doctor_list')


def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Approved'
    appointment.save()
    return redirect('appoinment_request')

def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Rejected'
    appointment.save()
    return redirect('appoinment_request')

@login_required
@user_passes_test(is_admin)
def patient_delete(request, id):
    patient = get_object_or_404(PatientProfile, id=id)

    # delete linked user → automatically deletes profile (CASCADE)
    user = patient.user
    user.delete()

    return redirect('patient_list')


@login_required
@user_passes_test(is_admin)
def patient_statistics(request):
    total_patients = PatientProfile.objects.count()

    gender_stats = PatientProfile.objects.values('gender').annotate(count=Count('gender'))

    age_stats = PatientProfile.objects.values('age').annotate(count=Count('age')).order_by('age')

    category_stats = PatientProfile.objects.values('category').annotate(count=Count('category'))

    appointment_stats = {
        'total': Appointment.objects.count(),
        'approved': Appointment.objects.filter(status='Approved').count(),
        'pending': Appointment.objects.filter(status='Pending').count(),
        'rejected': Appointment.objects.filter(status='Rejected').count(),
    }

    context = {
        'total_patients': total_patients,
        'gender_stats': gender_stats,
        'age_stats': age_stats,
        'category_stats': category_stats,
        'appointment_stats': appointment_stats,
    }

    return render(request, 'patient_statistics.html', context)



