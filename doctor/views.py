from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.contrib import messages

from patient.models import Appointment
from .models import DoctorProfile


# =========================
# HELPERS
# =========================

def is_doctor(user):
    """Allow only users in Doctor group"""
    return user.is_authenticated and user.groups.filter(name='Doctor').exists()


# =========================
# AUTHENTICATION
# =========================

def doctor_register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        specialization = request.POST.get('specialization')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'doctor_register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'doctor_register.html')

        user = User.objects.create_user(username=username, password=password)

        group, _ = Group.objects.get_or_create(name='Doctor')
        user.groups.add(group)

        DoctorProfile.objects.create(
            user=user,
            full_name=username,
            specialization=specialization
        )

        messages.success(request, "Doctor registered successfully. Please login.")
        return redirect('doctor_login')

    return render(request, 'doctor_register.html')


def doctor_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.groups.filter(name='Doctor').exists():
            login(request, user)
            return redirect('doctor_dashboard')

        messages.error(request, "Invalid credentials or access denied.")

    return render(request, 'logindoctor.html')


def doctor_logout_view(request):
    logout(request)
    return redirect('doctor_login')


# =========================
# DASHBOARD
# =========================

@login_required(login_url='doctor_login')
@user_passes_test(is_doctor, login_url='doctor_login')
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(
        doctor=request.user,
        status='Approved'
    ).order_by('appointment_date')

    return render(request, 'doctordashboard.html', {
        'appointments': appointments
    })


# =========================
# APPOINTMENT ACTIONS
# =========================

@login_required(login_url='doctor_login')
@user_passes_test(is_doctor, login_url='doctor_login')
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user
    )
    appointment.status = 'Rejected'
    appointment.save()

    messages.info(request, "Appointment rejected.")
    return redirect('doctor_dashboard')


@login_required(login_url='doctor_login')
@user_passes_test(is_doctor, login_url='doctor_login')
def complete_consultation(request, appointment_id):
    """
    Doctor completes consultation:
    - adds diagnosis
    - adds prescription
    - adds bill amount
    - moves appointment to Medical History
    """

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor=request.user
    )

    if request.method == "POST":
        appointment.diagnosis = request.POST.get('diagnosis')
        appointment.prescription = request.POST.get('prescription')
        appointment.bill_amount = request.POST.get('bill_amount')
        appointment.status = 'Completed'

        appointment.save()

        messages.success(
            request,
            f"Consultation for {appointment.patient.username} completed successfully."
        )
        return redirect('doctor_dashboard')

    return render(request, 'doctor/complete_consultation.html', {
        'appointment': appointment
    })

@login_required
def complete_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    appointment.status = 'Completed'
    appointment.save()

    messages.success(request, "Appointment completed successfully")
    return redirect('doctor_appointments')