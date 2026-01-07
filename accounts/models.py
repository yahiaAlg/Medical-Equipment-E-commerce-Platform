from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    USER_TYPES = [
        ("general", "Utilisateur général"),
        ("pharmacy", "Personnel de pharmacie"),
        ("clinic", "Personnel de clinique"),
        ("doctor", "Médecin"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="utilisateur",
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default="general",
        verbose_name="type d'utilisateur",
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="téléphone")
    address = models.TextField(blank=True, verbose_name="adresse")
    city = models.CharField(max_length=100, blank=True, verbose_name="ville")
    state = models.CharField(max_length=100, blank=True, verbose_name="état/province")
    zip_code = models.CharField(max_length=10, blank=True, verbose_name="code postal")
    country = models.CharField(max_length=100, blank=True, verbose_name="pays")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="photo de profil"
    )
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="date de naissance"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="modifié le")

    class Meta:
        verbose_name = "profil utilisateur"
        verbose_name_plural = "profils utilisateurs"

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


class PharmacyProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pharmacy_profile",
        verbose_name="utilisateur",
    )
    pharmacy_name = models.CharField(max_length=200, verbose_name="nom de la pharmacie")
    license_number = models.CharField(max_length=100, verbose_name="numéro de licence")
    license_expiry = models.DateField(verbose_name="date d'expiration de la licence")
    business_registration = models.CharField(
        max_length=100, verbose_name="numéro d'enregistrement commercial"
    )
    verified = models.BooleanField(default=False, verbose_name="vérifié")
    verification_documents = models.FileField(
        upload_to="pharmacy_docs/", blank=True, verbose_name="documents de vérification"
    )

    class Meta:
        verbose_name = "profil pharmacie"
        verbose_name_plural = "profils pharmacies"

    def __str__(self):
        return f"{self.pharmacy_name} - {self.license_number}"


class ClinicProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="clinic_profile",
        verbose_name="utilisateur",
    )
    clinic_name = models.CharField(max_length=200, verbose_name="nom de la clinique")
    department = models.CharField(max_length=100, verbose_name="département")
    employee_id = models.CharField(max_length=50, verbose_name="identifiant employé")
    position = models.CharField(max_length=100, verbose_name="poste")
    supervisor_email = models.EmailField(verbose_name="email du superviseur")
    budget_limit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="limite budgétaire"
    )

    class Meta:
        verbose_name = "profil clinique"
        verbose_name_plural = "profils cliniques"

    def __str__(self):
        return f"{self.clinic_name} - {self.department}"


class DoctorProfile(models.Model):
    SPECIALTIES = [
        ("dermatology", "Dermatologie"),
        ("ophthalmology", "Ophtalmologie"),
        ("nephrology", "Néphrologie"),
        ("cardiology", "Cardiologie"),
        ("orthopedics", "Orthopédie"),
        ("neurology", "Neurologie"),
        ("pediatrics", "Pédiatrie"),
        ("general", "Médecine générale"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        verbose_name="utilisateur",
    )
    medical_license = models.CharField(
        max_length=100, verbose_name="numéro de licence médicale"
    )
    specialty = models.CharField(
        max_length=50, choices=SPECIALTIES, verbose_name="spécialité"
    )
    years_of_experience = models.PositiveIntegerField(
        verbose_name="années d'expérience"
    )
    hospital_affiliation = models.CharField(
        max_length=200, verbose_name="hôpital d'affiliation"
    )
    credentials = models.TextField(verbose_name="diplômes et certifications")
    verified = models.BooleanField(default=False, verbose_name="vérifié")

    class Meta:
        verbose_name = "profil médecin"
        verbose_name_plural = "profils médecins"

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.get_specialty_display()}"
