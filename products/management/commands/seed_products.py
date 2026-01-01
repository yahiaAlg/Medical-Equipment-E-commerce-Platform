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

        # Create Categories based on HTML pages
        categories_data = [
            {
                "name": "Cardiology",
                "description": "Cardiovascular care equipment and supplies",
            },
            {
                "name": "Neurology",
                "description": "Neurological diagnostic and treatment equipment",
            },
            {
                "name": "Orthopedics",
                "description": "Bone, joint and muscle care equipment",
            },
            {
                "name": "Pediatrics",
                "description": "Specialized equipment for children and adolescents",
            },
            {
                "name": "Dermatology",
                "description": "Skin, hair and nail care equipment",
            },
            {
                "name": "Ophthalmology",
                "description": "Eye care and vision equipment",
            },
            {
                "name": "Surgery",
                "description": "Surgical instruments and equipment",
            },
            {
                "name": "Gastroenterology",
                "description": "Digestive system diagnostic and treatment equipment",
            },
            {
                "name": "Laboratory",
                "description": "Diagnostic testing and analysis equipment",
            },
            {
                "name": "Gynecology",
                "description": "Women's health and reproductive care equipment",
            },
            {
                "name": "Pneumology",
                "description": "Respiratory and lung disease equipment",
            },
            {
                "name": "Dentistry",
                "description": "Dental care and oral health equipment",
            },
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"], defaults={"description": cat_data["description"]}
            )
            categories[cat_data["name"]] = cat
            if created:
                self.stdout.write(f"Created category: {cat.name}")

        # Create Brands
        brands_data = [
            "3M Littmann",
            "Accu-Chek",
            "Omron",
            "Welch Allyn",
            "Philips",
            "MedTech Pro",
            "HealthLine",
            "CarePlus",
        ]

        brands = []
        for brand_name in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={"description": f"Leading manufacturer of medical equipment"},
            )
            brands.append(brand)

        # Create Products based on HTML pages
        products_data = [
            # Cardiology Products
            {
                "name": "ECG Electrodes",
                "category": "Cardiology",
                "price": 2600,
                "specialty": "cardiology",
                "description": "Disposable, pre-gelled electrodes for cardiac monitoring",
            },
            {
                "name": "Blood Lancets",
                "category": "Cardiology",
                "price": 4000,
                "specialty": "cardiology",
                "description": "Sterile, single-use lancets for blood sampling",
            },
            {
                "name": "CardioAspirine",
                "category": "Cardiology",
                "price": 200,
                "specialty": "cardiology",
                "description": "Low-dose aspirin for cardiovascular protection and blood thinning",
            },
            # Dentistry Products
            {
                "name": "Ledermix",
                "category": "Dentistry",
                "price": 2000,
                "specialty": "general",
                "description": "Prescription dental paste containing triamcinolone acetonide and chlortetracycline HCl",
            },
            {
                "name": "Oraqix",
                "category": "Dentistry",
                "price": 4000,
                "specialty": "general",
                "description": "Periodontal gel containing lidocaine and prilocaine for local anesthesia",
            },
            {
                "name": "Dental Scalers",
                "category": "Dentistry",
                "price": 3000,
                "specialty": "general",
                "description": "Set of dental instruments for removing plaque and tartar from teeth",
            },
            # Dermatology Products
            {
                "name": "Canestene DERM",
                "category": "Dermatology",
                "price": 1150,
                "specialty": "dermatology",
                "description": "Antifungal cream for treating skin infections like athlete's foot, ringworm, and fungal skin irritations",
            },
            {
                "name": "Dermo Cuivre",
                "category": "Dermatology",
                "price": 1400,
                "specialty": "dermatology",
                "description": "Skin repair ointment for treating minor wounds, burns, and skin irritations",
            },
            {
                "name": "Biafine",
                "category": "Dermatology",
                "price": 1700,
                "specialty": "dermatology",
                "description": "Soothing and protective skin care cream for irritated or damaged skin",
            },
            # Gastroenterology Products
            {
                "name": "Spascol LP",
                "category": "Gastroenterology",
                "price": 1150,
                "specialty": "general",
                "description": "Muscle relaxant medication for treating muscle spasms and pain",
            },
            {
                "name": "Gastricalm",
                "category": "Gastroenterology",
                "price": 850,
                "specialty": "general",
                "description": "Medication for treating stomach acid and heartburn",
            },
            {
                "name": "Anatomical Stomach Model",
                "category": "Gastroenterology",
                "price": 4500,
                "specialty": "general",
                "description": "Educational model of the human stomach",
            },
            # Gynecology Products
            {
                "name": "Femaferrin",
                "category": "Gynecology",
                "price": 2000,
                "specialty": "general",
                "description": "Iron supplement tablets for treating iron deficiency",
            },
            {
                "name": "Quality Suction Handle with Bottle",
                "category": "Gynecology",
                "price": 3000,
                "specialty": "general",
                "description": "Manual suction device with collection bottle",
            },
            {
                "name": "Anatomical Model (Female Reproductive System)",
                "category": "Gynecology",
                "price": 4500,
                "specialty": "general",
                "description": "Educational model of female reproductive anatomy",
            },
            # Laboratory Products
            {
                "name": "Microcentrifuge Tubes (1.5 ml)",
                "category": "Laboratory",
                "price": 3000,
                "specialty": "general",
                "description": "Rack of 96 blue-capped microcentrifuge tubes",
            },
            {
                "name": "Laboratory Glassware Set",
                "category": "Laboratory",
                "price": 2250,
                "specialty": "general",
                "description": "Set including beaker, graduated cylinder, and Erlenmeyer flask",
            },
            {
                "name": "Wash Bottle (500 ml)",
                "category": "Laboratory",
                "price": 550,
                "specialty": "general",
                "description": "Plastic wash bottle with squeezer top",
            },
            # Neurology Products
            {
                "name": "Reflex Hammer",
                "category": "Neurology",
                "price": 2000,
                "specialty": "neurology",
                "description": "Tool for testing patient reflexes",
            },
            {
                "name": "Lumbar Puncture Tray",
                "category": "Neurology",
                "price": 20000,
                "specialty": "neurology",
                "description": "Sterile kit for performing spinal taps and cerebrospinal fluid analysis",
            },
            {
                "name": "Neurobion Forte",
                "category": "Neurology",
                "price": 1500,
                "specialty": "neurology",
                "description": "Vitamin B complex supplement that helps relieve tingling, numbness, and weakness",
            },
            # Ophthalmology Products
            {
                "name": "Vibac",
                "category": "Ophthalmology",
                "price": 750,
                "specialty": "ophthalmology",
                "description": "Antiseptic solution for skin disinfection",
            },
            {
                "name": "Vabysmo",
                "category": "Ophthalmology",
                "price": 20000,
                "specialty": "ophthalmology",
                "description": "Injection solution containing 120 mg of active ingredient",
            },
            {
                "name": "Ophthavet",
                "category": "Ophthalmology",
                "price": 2250,
                "specialty": "ophthalmology",
                "description": "Ophthalmic solution for eye care",
            },
            # Orthopedics Products
            {
                "name": "Alvityl Chondroflex",
                "category": "Orthopedics",
                "price": 3250,
                "specialty": "orthopedics",
                "description": "Joint health supplement with chondroitin and glucosamine for maintaining cartilage and joint function",
            },
            {
                "name": "Structoflex",
                "category": "Orthopedics",
                "price": 4000,
                "specialty": "orthopedics",
                "description": "Joint supplement containing chondroitin sulfate for supporting joint mobility and cartilage health",
            },
            {
                "name": "Salusan Ortho",
                "category": "Orthopedics",
                "price": 2750,
                "specialty": "orthopedics",
                "description": "Orthopedic health supplement with collagen and vitamins to support bones and joints",
            },
            # Pediatrics Products
            {
                "name": "EfferalganMed Pédiatrique (Paracétamol 30 mg/ml)",
                "category": "Pediatrics",
                "price": 550,
                "specialty": "pediatrics",
                "description": "Pediatric paracetamol solution for pain and fever relief in children aged 4 to 32 kg",
            },
            {
                "name": "Melilax",
                "category": "Pediatrics",
                "price": 1600,
                "specialty": "pediatrics",
                "description": "Herbal laxative supplement for gentle relief of occasional constipation",
            },
            {
                "name": "Doliprane (Paracetamol)",
                "category": "Pediatrics",
                "price": 1000,
                "specialty": "pediatrics",
                "description": "Pain reliever and fever reducer containing paracetamol (acetaminophen)",
            },
            # Pneumology Products
            {
                "name": "Deslor (Desloratadine 5 mg)",
                "category": "Pneumology",
                "price": 1500,
                "specialty": "general",
                "description": "Antihistamine tablets for allergy relief",
            },
            {
                "name": "Peak Flow Meter",
                "category": "Pneumology",
                "price": 2250,
                "specialty": "general",
                "description": "Device for measuring respiratory flow rate",
            },
            {
                "name": "Nebulizer",
                "category": "Pneumology",
                "price": 4500,
                "specialty": "general",
                "description": "Electronic device for administering medication in mist form",
            },
            # Surgery Products
            {
                "name": "Surgical Instrument Set",
                "category": "Surgery",
                "price": 7500,
                "specialty": "general",
                "description": "Basic set of surgical instruments including forceps, scissors, and scalpel handles",
            },
            {
                "name": "Disposable Surgical Gloves",
                "category": "Surgery",
                "price": 1750,
                "specialty": "general",
                "description": "Box of sterile latex or nitrile examination gloves",
            },
            {
                "name": "Medical Tape",
                "category": "Surgery",
                "price": 350,
                "specialty": "general",
                "description": "Roll of hypoallergenic medical tape",
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
                    "sku": f"FEN-{1000 + idx}",
                    "stock_quantity": random.randint(10, 150),
                    "specialty": prod_data["specialty"],
                    "availability_status": "in_stock",
                    "short_description": prod_data["description"],
                    "description": f'{prod_data["description"]}. Professional-grade quality for medical use. Meets all medical standards and regulations.',
                    "specifications": "Professional medical grade\nWarranty: 1-2 years\nCertifications: Medical standards compliant",
                    "warranty": "Standard manufacturer warranty",
                    "featured": random.choice([True, False]),
                    "trending": random.choice([True, False]),
                },
            )

            if created:
                self.stdout.write(f"Created product: {product.name}")

                # Add placeholder images
                for img_num in range(3):
                    image_url = f"https://source.unsplash.com/800x600/?medical,{prod_data['category'].lower()}&sig={idx}{img_num}"

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

        # Create sample reviews
        users = User.objects.all()
        if users.exists():
            products = Product.objects.all()[:15]
            review_titles = [
                "Excellent quality",
                "Great product",
                "Highly recommended",
                "Perfect for our clinic",
                "Professional grade equipment",
                "Very satisfied",
                "Good value for money",
            ]

            for product in products:
                user = random.choice(users)
                ProductReview.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={
                        "rating": random.randint(4, 5),
                        "title": random.choice(review_titles),
                        "comment": "Very satisfied with this purchase. High quality and reliable.",
                        "verified_purchase": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded products!"))
