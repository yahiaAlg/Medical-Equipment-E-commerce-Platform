from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPES = [
        ('general', 'General User'),
        ('pharmacy', 'Pharmacy Personnel'),
        ('clinic', 'Clinic Staff'),
        ('doctor', 'Doctor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='general')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

class PharmacyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacy_profile')
    pharmacy_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100)
    license_expiry = models.DateField()
    business_registration = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    verification_documents = models.FileField(upload_to='pharmacy_docs/', blank=True)
    
    def __str__(self):
        return f"{self.pharmacy_name} - {self.license_number}"

class ClinicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='clinic_profile')
    clinic_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50)
    position = models.CharField(max_length=100)
    supervisor_email = models.EmailField()
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.clinic_name} - {self.department}"

class DoctorProfile(models.Model):
    SPECIALTIES = [
        ('dermatology', 'Dermatology'),
        ('ophthalmology', 'Ophthalmology'),
        ('nephrology', 'Nephrology'),
        ('cardiology', 'Cardiology'),
        ('orthopedics', 'Orthopedics'),
        ('neurology', 'Neurology'),
        ('pediatrics', 'Pediatrics'),
        ('general', 'General Medicine'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    medical_license = models.CharField(max_length=100)
    specialty = models.CharField(max_length=50, choices=SPECIALTIES)
    years_of_experience = models.PositiveIntegerField()
    hospital_affiliation = models.CharField(max_length=200)
    credentials = models.TextField()
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.get_specialty_display()}"