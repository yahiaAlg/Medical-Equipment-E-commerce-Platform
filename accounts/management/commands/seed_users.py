from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import UserProfile, PharmacyProfile, ClinicProfile, DoctorProfile
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Seeds user profiles data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding users and profiles...")

        # Create demo users
        users_data = [
            {
                "username": "demo_general",
                "email": "general@demo.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "demo123456",
                "profile_type": "general",
            },
            {
                "username": "demo_pharmacy",
                "email": "pharmacy@demo.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "password": "demo123456",
                "profile_type": "pharmacy",
            },
            {
                "username": "demo_clinic",
                "email": "clinic@demo.com",
                "first_name": "Michael",
                "last_name": "Chen",
                "password": "demo123456",
                "profile_type": "clinic",
            },
            {
                "username": "demo_doctor",
                "email": "doctor@demo.com",
                "first_name": "Emily",
                "last_name": "Williams",
                "password": "demo123456",
                "profile_type": "doctor",
            },
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                },
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(f"Created user: {user.username}")

            # Create UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "user_type": user_data["profile_type"],
                    "phone": f"+1-555-{random.randint(1000, 9999)}",
                    "address": f"{random.randint(100, 9999)} Main Street",
                    "city": random.choice(
                        ["New York", "Los Angeles", "Chicago", "Houston"]
                    ),
                    "state": random.choice(["NY", "CA", "IL", "TX"]),
                    "zip_code": f"{random.randint(10000, 99999)}",
                    "country": "USA",
                    "date_of_birth": date.today()
                    - timedelta(days=random.randint(10000, 20000)),
                },
            )

            # Create specific profiles
            if user_data["profile_type"] == "pharmacy":
                PharmacyProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "pharmacy_name": "HealthCare Pharmacy",
                        "license_number": f"PH{random.randint(100000, 999999)}",
                        "license_expiry": date.today() + timedelta(days=365),
                        "business_registration": f"BR{random.randint(100000, 999999)}",
                        "verified": True,
                    },
                )

            elif user_data["profile_type"] == "clinic":
                ClinicProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "clinic_name": "Central Medical Clinic",
                        "department": "Procurement",
                        "employee_id": f"EMP{random.randint(1000, 9999)}",
                        "position": "Purchasing Manager",
                        "supervisor_email": "supervisor@centralmedical.com",
                        "budget_limit": 50000.00,
                    },
                )

            elif user_data["profile_type"] == "doctor":
                DoctorProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "medical_license": f"MD{random.randint(100000, 999999)}",
                        "specialty": "cardiology",
                        "years_of_experience": 12,
                        "hospital_affiliation": "City General Hospital",
                        "credentials": "MD, FACC, Board Certified in Cardiology",
                        "verified": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded users and profiles!"))
