from django.contrib import admin
from .models import UserProfile, PharmacyProfile, ClinicProfile, DoctorProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_type", "phone", "city", "state", "created_at")
    list_filter = ("user_type", "country", "state", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone",
        "city",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Informations utilisateur",
            {"fields": ("user", "user_type", "avatar", "date_of_birth")},
        ),
        (
            "Coordonnées",
            {"fields": ("phone", "address", "city", "state", "zip_code", "country")},
        ),
        (
            "Horodatage",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(PharmacyProfile)
class PharmacyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "pharmacy_name",
        "user",
        "license_number",
        "license_expiry",
        "verified",
    )
    list_filter = ("verified", "license_expiry")
    search_fields = (
        "pharmacy_name",
        "license_number",
        "business_registration",
        "user__username",
    )
    readonly_fields = ("user",)
    list_editable = ("verified",)

    fieldsets = (
        ("Utilisateur", {"fields": ("user",)}),
        (
            "Informations pharmacie",
            {
                "fields": (
                    "pharmacy_name",
                    "license_number",
                    "license_expiry",
                    "business_registration",
                )
            },
        ),
        ("Vérification", {"fields": ("verified", "verification_documents")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(ClinicProfile)
class ClinicProfileAdmin(admin.ModelAdmin):
    list_display = (
        "clinic_name",
        "user",
        "department",
        "employee_id",
        "position",
        "budget_limit",
    )
    list_filter = ("department", "position")
    search_fields = (
        "clinic_name",
        "department",
        "employee_id",
        "user__username",
        "supervisor_email",
    )
    readonly_fields = ("user",)

    fieldsets = (
        ("Utilisateur", {"fields": ("user",)}),
        (
            "Informations clinique",
            {"fields": ("clinic_name", "department", "position")},
        ),
        (
            "Détails d'emploi",
            {"fields": ("employee_id", "supervisor_email", "budget_limit")},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "specialty",
        "medical_license",
        "years_of_experience",
        "hospital_affiliation",
        "verified",
    )
    list_filter = ("specialty", "verified", "years_of_experience")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "medical_license",
        "hospital_affiliation",
    )
    readonly_fields = ("user",)
    list_editable = ("verified",)

    fieldsets = (
        ("Utilisateur", {"fields": ("user",)}),
        (
            "Informations professionnelles",
            {
                "fields": (
                    "medical_license",
                    "specialty",
                    "years_of_experience",
                    "hospital_affiliation",
                )
            },
        ),
        ("Diplômes et vérification", {"fields": ("credentials", "verified")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
