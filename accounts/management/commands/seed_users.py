from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import UserProfile, PharmacyProfile, ClinicProfile, DoctorProfile
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Initialise les données des profils utilisateurs"

    def handle(self, *args, **kwargs):
        self.stdout.write("Initialisation des utilisateurs et profils...")

        # Créer des utilisateurs de démonstration
        users_data = [
            {
                "username": "demo_general",
                "email": "general@demo.com",
                "first_name": "Jean",
                "last_name": "Dupont",
                "password": "demo123456",
                "profile_type": "general",
            },
            {
                "username": "demo_pharmacy",
                "email": "pharmacy@demo.com",
                "first_name": "Sophie",
                "last_name": "Martin",
                "password": "demo123456",
                "profile_type": "pharmacy",
            },
            {
                "username": "demo_clinic",
                "email": "clinic@demo.com",
                "first_name": "Pierre",
                "last_name": "Dubois",
                "password": "demo123456",
                "profile_type": "clinic",
            },
            {
                "username": "demo_doctor",
                "email": "doctor@demo.com",
                "first_name": "Marie",
                "last_name": "Bernard",
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
                self.stdout.write(f"Utilisateur créé : {user.username}")

            # Créer le profil utilisateur
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "user_type": user_data["profile_type"],
                    "phone": f"+33-{random.randint(1, 9)}-{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
                    "address": f"{random.randint(1, 999)} rue {random.choice(['de la République', 'Victor Hugo', 'Pasteur', 'Gambetta'])}",
                    "city": random.choice(
                        ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes"]
                    ),
                    "state": random.choice(
                        [
                            "Île-de-France",
                            "Auvergne-Rhône-Alpes",
                            "Provence-Alpes-Côte d'Azur",
                            "Occitanie",
                        ]
                    ),
                    "zip_code": f"{random.randint(10000, 99999)}",
                    "country": "France",
                    "date_of_birth": date.today()
                    - timedelta(days=random.randint(10000, 20000)),
                },
            )

            # Créer les profils spécifiques
            if user_data["profile_type"] == "pharmacy":
                PharmacyProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "pharmacy_name": "Pharmacie de la Santé",
                        "license_number": f"PH{random.randint(100000, 999999)}",
                        "license_expiry": date.today() + timedelta(days=365),
                        "business_registration": f"SIRET-{random.randint(100000000, 999999999)}",
                        "verified": True,
                    },
                )

            elif user_data["profile_type"] == "clinic":
                ClinicProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "clinic_name": "Clinique Médicale Centrale",
                        "department": "Achats et Approvisionnement",
                        "employee_id": f"EMP{random.randint(1000, 9999)}",
                        "position": "Responsable des Achats",
                        "supervisor_email": "superviseur@cliniquecentrale.fr",
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
                        "hospital_affiliation": "Hôpital Général de la Ville",
                        "credentials": "Docteur en Médecine, Spécialiste en Cardiologie, Certifié par l'Ordre des Médecins",
                        "verified": True,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS("Utilisateurs et profils initialisés avec succès !")
        )
