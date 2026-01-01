from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create admin superuser with predefined credentials"

    def handle(self, *args, **options):
        username = "admin"
        password = "system2026"
        email = "admin@system.com"

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Admin user "{username}" already exists. Skipping creation.'
                )
            )
            return

        try:
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created admin superuser: {username}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating admin user: {str(e)}"))
