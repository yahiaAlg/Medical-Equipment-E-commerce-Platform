from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from ...models import (
    Category,
    Brand,
    Product,
    ProductImage,
    ProductReview,
)
from django.contrib.auth.models import User
import requests
import random
from decimal import Decimal


class Command(BaseCommand):
    help = "Seeds products, categories, brands, and images"

    def download_image(self, url):
        """Helper to download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content)
        except:
            pass
        return None

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding products...")

        # Create Categories
        categories_data = [
            {
                "name": "Diagnostic Equipment",
                "description": "Medical diagnostic tools and equipment",
            },
            {
                "name": "Surgical Instruments",
                "description": "High-quality surgical tools",
            },
            {
                "name": "Patient Monitoring",
                "description": "Vital signs and patient monitoring devices",
            },
            {
                "name": "Laboratory Equipment",
                "description": "Lab testing and analysis equipment",
            },
            {
                "name": "Imaging Systems",
                "description": "Medical imaging and radiology equipment",
            },
            {
                "name": "Therapeutic Equipment",
                "description": "Treatment and therapy devices",
            },
            {
                "name": "Emergency Care",
                "description": "Emergency and critical care equipment",
            },
            {
                "name": "Sterilization",
                "description": "Sterilization and infection control equipment",
            },
        ]

        categories = []
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"], defaults={"description": cat_data["description"]}
            )
            categories.append(cat)
            if created:
                self.stdout.write(f"Created category: {cat.name}")

        # Create Brands
        brands_data = [
            "MedTech Pro",
            "HealthLine",
            "PrecisionMed",
            "CarePlus",
            "VitalCare",
            "MediCore",
            "ProHealth",
            "EliteMed",
        ]

        brands = []
        for brand_name in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={"description": f"Leading manufacturer of medical equipment"},
            )
            brands.append(brand)

        # Create Products
        products_data = [
            # Diagnostic Equipment
            {
                "name": "Digital Stethoscope Pro",
                "category": 0,
                "price": 299.99,
                "specialty": "cardiology",
            },
            {
                "name": "Pulse Oximeter Advanced",
                "category": 0,
                "price": 89.99,
                "specialty": "general",
            },
            {
                "name": "Digital Thermometer Set",
                "category": 0,
                "price": 49.99,
                "specialty": "general",
            },
            {
                "name": "Blood Pressure Monitor",
                "category": 0,
                "price": 129.99,
                "specialty": "cardiology",
            },
            # Surgical Instruments
            {
                "name": "Surgical Scissors Set",
                "category": 1,
                "price": 159.99,
                "specialty": "general",
            },
            {
                "name": "Scalpel Handle Kit",
                "category": 1,
                "price": 79.99,
                "specialty": "general",
            },
            {
                "name": "Surgical Forceps Collection",
                "category": 1,
                "price": 199.99,
                "specialty": "general",
            },
            {
                "name": "Needle Holder Set",
                "category": 1,
                "price": 139.99,
                "specialty": "general",
            },
            # Patient Monitoring
            {
                "name": "ECG Machine 12-Lead",
                "category": 2,
                "price": 2499.99,
                "specialty": "cardiology",
            },
            {
                "name": "Patient Monitor Bedside",
                "category": 2,
                "price": 1899.99,
                "specialty": "general",
            },
            {
                "name": "Fetal Doppler Monitor",
                "category": 2,
                "price": 399.99,
                "specialty": "pediatrics",
            },
            {
                "name": "Holter Monitor System",
                "category": 2,
                "price": 1299.99,
                "specialty": "cardiology",
            },
            # Laboratory Equipment
            {
                "name": "Centrifuge Machine",
                "category": 3,
                "price": 1599.99,
                "specialty": "general",
            },
            {
                "name": "Microscope Digital",
                "category": 3,
                "price": 899.99,
                "specialty": "general",
            },
            {
                "name": "Laboratory Incubator",
                "category": 3,
                "price": 1299.99,
                "specialty": "general",
            },
            {
                "name": "PCR Thermal Cycler",
                "category": 3,
                "price": 3999.99,
                "specialty": "general",
            },
            # Imaging Systems
            {
                "name": "Ultrasound Machine Portable",
                "category": 4,
                "price": 4999.99,
                "specialty": "general",
            },
            {
                "name": "X-Ray Film Viewer LED",
                "category": 4,
                "price": 299.99,
                "specialty": "orthopedics",
            },
            {
                "name": "Dental X-Ray System",
                "category": 4,
                "price": 3499.99,
                "specialty": "general",
            },
            {
                "name": "Endoscope Camera System",
                "category": 4,
                "price": 2799.99,
                "specialty": "general",
            },
            # Therapeutic Equipment
            {
                "name": "Nebulizer Machine",
                "category": 5,
                "price": 149.99,
                "specialty": "general",
            },
            {
                "name": "TENS Unit Professional",
                "category": 5,
                "price": 189.99,
                "specialty": "orthopedics",
            },
            {
                "name": "Infusion Pump",
                "category": 5,
                "price": 1799.99,
                "specialty": "general",
            },
            {
                "name": "Oxygen Concentrator",
                "category": 5,
                "price": 599.99,
                "specialty": "general",
            },
            # Emergency Care
            {
                "name": "AED Defibrillator",
                "category": 6,
                "price": 1499.99,
                "specialty": "cardiology",
            },
            {
                "name": "Emergency Crash Cart",
                "category": 6,
                "price": 2999.99,
                "specialty": "general",
            },
            {
                "name": "Suction Machine Portable",
                "category": 6,
                "price": 399.99,
                "specialty": "general",
            },
            {
                "name": "Emergency Oxygen Kit",
                "category": 6,
                "price": 699.99,
                "specialty": "general",
            },
            # Sterilization
            {
                "name": "Autoclave Sterilizer",
                "category": 7,
                "price": 2199.99,
                "specialty": "general",
            },
            {
                "name": "UV Sterilization Cabinet",
                "category": 7,
                "price": 799.99,
                "specialty": "general",
            },
        ]

        for idx, prod_data in enumerate(products_data):
            product, created = Product.objects.get_or_create(
                name=prod_data["name"],
                defaults={
                    "category": categories[prod_data["category"]],
                    "brand": random.choice(brands),
                    "price": Decimal(str(prod_data["price"])),
                    "bulk_price": Decimal(str(prod_data["price"] * 0.85)),
                    "bulk_quantity": 10,
                    "sku": f"MED-{1000 + idx}",
                    "stock_quantity": random.randint(5, 100),
                    "specialty": prod_data["specialty"],
                    "availability_status": "in_stock",
                    "short_description": f'Professional-grade {prod_data["name"].lower()} for medical use',
                    "description": f'High-quality {prod_data["name"]} designed for healthcare professionals. Features advanced technology and reliable performance. Meets all medical standards and regulations.',
                    "specifications": "Dimensions: Standard medical grade\nWarranty: 2 years\nCertifications: FDA, CE",
                    "warranty": "2 years manufacturer warranty",
                    "featured": random.choice([True, False]),
                    "trending": random.choice([True, False]),
                },
            )

            if created:
                self.stdout.write(f"Created product: {product.name}")

                # Download and add 3 images per product
                for img_num in range(3):
                    # Using Unsplash Source for medical equipment images
                    # Using random seeds for variety
                    image_url = f"https://source.unsplash.com/800x600/?medical,equipment&sig={idx}{img_num}"

                    image_content = self.download_image(image_url)
                    if image_content:
                        ProductImage.objects.create(
                            product=product,
                            image=ContentFile(
                                image_content.read(),
                                name=f"{product.slug}_{img_num}.jpg",
                            ),
                            alt_text=f"{product.name} - Image {img_num + 1}",
                            is_primary=(img_num == 0),
                        )
                        self.stdout.write(
                            f"  Added image {img_num + 1} for {product.name}"
                        )

        # Create sample reviews
        users = User.objects.all()
        if users.exists():
            products = Product.objects.all()[:10]
            for product in products:
                user = random.choice(users)
                ProductReview.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={
                        "rating": random.randint(4, 5),
                        "title": random.choice(
                            [
                                "Excellent quality",
                                "Great product",
                                "Highly recommended",
                                "Perfect for our clinic",
                                "Professional grade equipment",
                            ]
                        ),
                        "comment": "Very satisfied with this purchase. High quality and reliable.",
                        "verified_purchase": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded products!"))
