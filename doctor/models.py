from django.db import models
from django.contrib.auth.models import User

# =========================
# Doctor Profile
# =========================
class DoctorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    full_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialization})"


# =========================
# Appointment Model
# =========================
class Appointment(models.Model):

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )

    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_appointments'
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    doctor_type = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    diagnosis = models.TextField(null=True, blank=True)
    prescription = models.TextField(null=True, blank=True)

    bill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bill_number = models.CharField(max_length=50, null=True, blank=True)

    payment_status = models.CharField(max_length=20, default='Not Paid')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment #{self.id} - {self.patient.username}"