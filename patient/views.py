from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from .models import Appointment, PatientProfile
import stripe

# Stripe setup (SERVER SIDE ONLY)
stripe.api_key = settings.STRIPE_SECRET_KEY


# -----------------------------
# 1. DASHBOARD
# -----------------------------
@login_required
def dashboard(request):
    profile = PatientProfile.objects.filter(user=request.user).first()
    return render(request, 'dashboard.html', {'profile': profile})


# -----------------------------
# 2. AUTHENTICATION
# -----------------------------
def patient_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if hasattr(user, 'doctor_profile'):
                return redirect('doctor_dashboard')
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'loginpatient.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, password=password)

        PatientProfile.objects.create(
            user=user,
            full_name=request.POST.get('full_name'),
            age=request.POST.get('age'),
            gender=request.POST.get('gender'),
            place=request.POST.get('place'),
            category=request.POST.get('category')
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html')


def patient_logout_view(request):
    logout(request)
    return redirect('login')


# -----------------------------
# 3. APPOINTMENTS
# -----------------------------
@login_required
def book_appointment(request):
    from doctor.models import DoctorProfile  # prevent circular import

    if request.method == "POST":
        Appointment.objects.create(
            patient=request.user,
            doctor_type=request.POST.get('doctor_type'),
            appointment_date=request.POST.get('date'),
            appointment_time=request.POST.get('time'),
            status='Pending',
            payment_status='Not Paid'
        )

        messages.success(request, "Appointment booked successfully")
        return redirect('patient_dashboard')

    doctors = DoctorProfile.objects.all().select_related('user')
    return render(request, 'book_appointment.html', {'doctors': doctors})


@login_required
def view_appointment(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'view_appointemnt.html', {'appointments': appointments})


# -----------------------------
# 4. BILLING & PAYMENTS
# -----------------------------
@login_required
def view_bills(request):
    bills = Appointment.objects.filter(
        patient=request.user,
        status='Completed'
    )

    total_due = sum(
        bill.bill_amount for bill in bills if bill.payment_status != 'Paid'
    )

    return render(request, 'view_bills.html', {
        'bills': bills,
        'total_due': total_due
    })


@login_required
def pay_bill(request, id):
    appointment = get_object_or_404(
        Appointment,
        id=id,
        patient=request.user
    )

    if appointment.payment_status == 'Paid':
        messages.info(request, "This bill is already paid")
        return redirect('view_bills')

    if request.method == "POST":
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f"Hospital Appointment - {appointment.doctor_type}",
                    },
                    'unit_amount': int(appointment.bill_amount * 100),
                },
                'quantity': 1,
            }],
            success_url=request.build_absolute_uri(
                reverse('payment_success', args=[appointment.id])
            ),
            # cancel_url=request.build_absolute_uri(
            #     reverse('payment_cancel', args=[appointment.id])
            # ),
        )

        return redirect(session.url, code=303)

    return render(request, 'pay_bill.html', {
        'appointment': appointment,
        'stripe_key': settings.STRIPE_PUBLISHABLE_KEY
    })


@login_required
def payment_success(request, id):
    appointment = get_object_or_404(
        Appointment,
        id=id,
        patient=request.user
    )

    # Mark payment as paid
    appointment.payment_status = 'Paid'
    appointment.save()

    return render(request, 'pyementSucess.html', {
        'appointment': appointment
    })


# -----------------------------
# 5. MEDICAL HISTORY & PROFILE
# -----------------------------
@login_required
def view_medical_history(request):
    history = Appointment.objects.filter(
        patient=request.user,
        status='Completed'
    ).order_by('-appointment_date')

    return render(request, 'view_medical_history.html', {
        'history': history
    })


@login_required
def update_profile(request):
    profile = get_object_or_404(PatientProfile, user=request.user)

    if request.method == "POST":
        profile.full_name = request.POST.get('full_name')
        profile.age = request.POST.get('age')
        profile.gender = request.POST.get('gender')
        profile.place = request.POST.get('place')
        profile.category = request.POST.get('category')
        profile.save()

        messages.success(request, "Profile updated successfully")
        return redirect('patient_dashboard')

    return render(request, 'update_profile.html', {'profile': profile})