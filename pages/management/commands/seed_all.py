from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Seeds all data in correct order"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting complete database seeding..."))

        commands = [
            ("seed_users", "User profiles"),
            ("seed_products", "Products and categories"),
            ("seed_contact", "Contact and support data"),
            ("seed_orders", "Orders and carts"),
        ]

        for cmd, description in commands:
            self.stdout.write(self.style.MIGRATE_HEADING(f'\n{"="*50}'))
            self.stdout.write(self.style.MIGRATE_HEADING(f"Seeding: {description}"))
            self.stdout.write(self.style.MIGRATE_HEADING(f'{"="*50}\n'))

            try:
                call_command(cmd)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in {cmd}: {str(e)}"))
                continue

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 50))
        self.stdout.write(self.style.SUCCESS("DATABASE SEEDING COMPLETE!"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write("\nDemo accounts created:")
        self.stdout.write("  • General User:  demo_general / demo123456")
        self.stdout.write("  • Pharmacy:      demo_pharmacy / demo123456")
        self.stdout.write("  • Clinic:        demo_clinic / demo123456")
        self.stdout.write("  • Doctor:        demo_doctor / demo123456")
