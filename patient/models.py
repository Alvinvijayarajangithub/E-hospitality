from django.db import models
from django.contrib.auth.models import User


class Appointment(models.Model):

    # ---------------- STATUS ----------------
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_CHOICES = [
        ('Not Paid', 'Not Paid'),
        ('Paid', 'Paid'),
    ]

    # ---------------- RELATIONS ----------------
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient'
    )

    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments_as_doctor'
    )

    # ---------------- APPOINTMENT DETAILS ----------------
    doctor_type = models.CharField(max_length=100)   # Department
    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # ---------------- CLINICAL DETAILS ----------------
    diagnosis = models.TextField(null=True, blank=True)
    prescription = models.TextField(null=True, blank=True)

    # ---------------- BILLING ----------------
    bill_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='Not Paid'
    )

    # ---------------- OTP PAYMENT (QR FLOW) ----------------
    otp = models.CharField(
        max_length=6,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.doctor_type} ({self.status})"


# =========================================================
# PATIENT PROFILE
# =========================================================

class PatientProfile(models.Model):

    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('Senior', 'Senior'),
        ('Child', 'Child'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    place = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.full_name