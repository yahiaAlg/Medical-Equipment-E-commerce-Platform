from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from ...models import (
    Category,
    Brand,
    Product,
    ProductImage,
    ProductReview,
    ProductVariant,
)
from django.contrib.auth.models import User
import requests
import random
from decimal import Decimal


class Command(BaseCommand):
    help = "Seeds products, categories, brands, images, and variants"

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
                "variants": [
                    {"title": "Pack Size", "value": "50 Pack", "cost": 0},
                    {"title": "Pack Size", "value": "100 Pack", "cost": 1500},
                    {"title": "Pack Size", "value": "200 Pack", "cost": 2800},
                ],
            },
            {
                "name": "Blood Lancets",
                "category": "Cardiology",
                "price": 4000,
                "specialty": "cardiology",
                "description": "Sterile, single-use lancets for blood sampling",
                "variants": [
                    {"title": "Gauge", "value": "28G", "cost": 0},
                    {"title": "Gauge", "value": "30G", "cost": 200},
                    {"title": "Quantity", "value": "100 pcs", "cost": 0},
                    {"title": "Quantity", "value": "200 pcs", "cost": 1800},
                ],
            },
            {
                "name": "CardioAspirine",
                "category": "Cardiology",
                "price": 200,
                "specialty": "cardiology",
                "description": "Low-dose aspirin for cardiovascular protection and blood thinning",
                "variants": [
                    {"title": "Dosage", "value": "75mg", "cost": 0},
                    {"title": "Dosage", "value": "100mg", "cost": 50},
                    {"title": "Pack Size", "value": "30 tablets", "cost": 0},
                    {"title": "Pack Size", "value": "60 tablets", "cost": 150},
                ],
            },
            # Dentistry Products
            {
                "name": "Ledermix",
                "category": "Dentistry",
                "price": 2000,
                "specialty": "general",
                "description": "Prescription dental paste containing triamcinolone acetonide and chlortetracycline HCl",
                "variants": [
                    {"title": "Size", "value": "5g tube", "cost": 0},
                    {"title": "Size", "value": "10g tube", "cost": 800},
                ],
            },
            {
                "name": "Oraqix",
                "category": "Dentistry",
                "price": 4000,
                "specialty": "general",
                "description": "Periodontal gel containing lidocaine and prilocaine for local anesthesia",
                "variants": [
                    {"title": "Volume", "value": "1.7g cartridge", "cost": 0},
                    {"title": "Pack", "value": "Single", "cost": 0},
                    {"title": "Pack", "value": "Box of 20", "cost": 15000},
                ],
            },
            {
                "name": "Dental Scalers",
                "category": "Dentistry",
                "price": 3000,
                "specialty": "general",
                "description": "Set of dental instruments for removing plaque and tartar from teeth",
                "variants": [
                    {"title": "Set Type", "value": "Basic (3 pieces)", "cost": 0},
                    {
                        "title": "Set Type",
                        "value": "Professional (6 pieces)",
                        "cost": 2000,
                    },
                    {
                        "title": "Set Type",
                        "value": "Complete (12 pieces)",
                        "cost": 4500,
                    },
                ],
            },
            # Dermatology Products
            {
                "name": "Canestene DERM",
                "category": "Dermatology",
                "price": 1150,
                "specialty": "dermatology",
                "description": "Antifungal cream for treating skin infections like athlete's foot, ringworm, and fungal skin irritations",
                "variants": [
                    {"title": "Size", "value": "15g", "cost": 0},
                    {"title": "Size", "value": "30g", "cost": 600},
                    {"title": "Size", "value": "50g", "cost": 1000},
                ],
            },
            {
                "name": "Dermo Cuivre",
                "category": "Dermatology",
                "price": 1400,
                "specialty": "dermatology",
                "description": "Skin repair ointment for treating minor wounds, burns, and skin irritations",
                "variants": [
                    {"title": "Volume", "value": "20ml", "cost": 0},
                    {"title": "Volume", "value": "50ml", "cost": 800},
                ],
            },
            {
                "name": "Biafine",
                "category": "Dermatology",
                "price": 1700,
                "specialty": "dermatology",
                "description": "Soothing and protective skin care cream for irritated or damaged skin",
                "variants": [
                    {"title": "Size", "value": "93g tube", "cost": 0},
                    {"title": "Size", "value": "186g tube", "cost": 1500},
                ],
            },
            # Gastroenterology Products
            {
                "name": "Spascol LP",
                "category": "Gastroenterology",
                "price": 1150,
                "specialty": "general",
                "description": "Muscle relaxant medication for treating muscle spasms and pain",
                "variants": [
                    {"title": "Pack Size", "value": "20 tablets", "cost": 0},
                    {"title": "Pack Size", "value": "40 tablets", "cost": 900},
                ],
            },
            {
                "name": "Gastricalm",
                "category": "Gastroenterology",
                "price": 850,
                "specialty": "general",
                "description": "Medication for treating stomach acid and heartburn",
                "variants": [
                    {"title": "Form", "value": "Tablets", "cost": 0},
                    {"title": "Form", "value": "Suspension", "cost": 200},
                ],
            },
            {
                "name": "Anatomical Stomach Model",
                "category": "Gastroenterology",
                "price": 4500,
                "specialty": "general",
                "description": "Educational model of the human stomach",
                "variants": [
                    {"title": "Size", "value": "Standard", "cost": 0},
                    {"title": "Size", "value": "Large (Teaching)", "cost": 2000},
                ],
            },
            # Gynecology Products
            {
                "name": "Femaferrin",
                "category": "Gynecology",
                "price": 2000,
                "specialty": "general",
                "description": "Iron supplement tablets for treating iron deficiency",
                "variants": [
                    {"title": "Pack", "value": "30 tablets", "cost": 0},
                    {"title": "Pack", "value": "60 tablets", "cost": 1700},
                    {"title": "Pack", "value": "90 tablets", "cost": 2400},
                ],
            },
            {
                "name": "Quality Suction Handle with Bottle",
                "category": "Gynecology",
                "price": 3000,
                "specialty": "general",
                "description": "Manual suction device with collection bottle",
                "variants": [
                    {"title": "Bottle Size", "value": "500ml", "cost": 0},
                    {"title": "Bottle Size", "value": "1000ml", "cost": 800},
                ],
            },
            {
                "name": "Anatomical Model (Female Reproductive System)",
                "category": "Gynecology",
                "price": 4500,
                "specialty": "general",
                "description": "Educational model of female reproductive anatomy",
                "variants": [
                    {"title": "Type", "value": "Standard", "cost": 0},
                    {
                        "title": "Type",
                        "value": "Detailed (with pathologies)",
                        "cost": 2500,
                    },
                ],
            },
            # Laboratory Products
            {
                "name": "Microcentrifuge Tubes (1.5 ml)",
                "category": "Laboratory",
                "price": 3000,
                "specialty": "general",
                "description": "Rack of 96 blue-capped microcentrifuge tubes",
                "variants": [
                    {"title": "Quantity", "value": "96 tubes (1 rack)", "cost": 0},
                    {"title": "Quantity", "value": "480 tubes (5 racks)", "cost": 2500},
                    {"title": "Color", "value": "Blue", "cost": 0},
                    {"title": "Color", "value": "Clear", "cost": 0},
                    {"title": "Color", "value": "Assorted", "cost": 200},
                ],
            },
            {
                "name": "Laboratory Glassware Set",
                "category": "Laboratory",
                "price": 2250,
                "specialty": "general",
                "description": "Set including beaker, graduated cylinder, and Erlenmeyer flask",
                "variants": [
                    {"title": "Set", "value": "Basic (3 pieces)", "cost": 0},
                    {"title": "Set", "value": "Standard (6 pieces)", "cost": 1500},
                    {"title": "Set", "value": "Professional (12 pieces)", "cost": 3000},
                ],
            },
            {
                "name": "Wash Bottle (500 ml)",
                "category": "Laboratory",
                "price": 550,
                "specialty": "general",
                "description": "Plastic wash bottle with squeezer top",
                "variants": [
                    {"title": "Volume", "value": "250ml", "cost": -200},
                    {"title": "Volume", "value": "500ml", "cost": 0},
                    {"title": "Volume", "value": "1000ml", "cost": 300},
                ],
            },
            # Neurology Products
            {
                "name": "Reflex Hammer",
                "category": "Neurology",
                "price": 2000,
                "specialty": "neurology",
                "description": "Tool for testing patient reflexes",
                "variants": [
                    {"title": "Type", "value": "Taylor", "cost": 0},
                    {"title": "Type", "value": "Buck", "cost": 300},
                    {"title": "Type", "value": "Babinski", "cost": 500},
                ],
            },
            {
                "name": "Lumbar Puncture Tray",
                "category": "Neurology",
                "price": 20000,
                "specialty": "neurology",
                "description": "Sterile kit for performing spinal taps and cerebrospinal fluid analysis",
                "variants": [
                    {"title": "Needle Size", "value": "20G", "cost": 0},
                    {"title": "Needle Size", "value": "22G", "cost": 500},
                    {"title": "Needle Size", "value": "25G", "cost": 1000},
                ],
            },
            {
                "name": "Neurobion Forte",
                "category": "Neurology",
                "price": 1500,
                "specialty": "neurology",
                "description": "Vitamin B complex supplement that helps relieve tingling, numbness, and weakness",
                "variants": [
                    {"title": "Pack", "value": "30 tablets", "cost": 0},
                    {"title": "Pack", "value": "60 tablets", "cost": 1300},
                ],
            },
            # Ophthalmology Products
            {
                "name": "Vibac",
                "category": "Ophthalmology",
                "price": 750,
                "specialty": "ophthalmology",
                "description": "Antiseptic solution for skin disinfection",
                "variants": [
                    {"title": "Volume", "value": "100ml", "cost": 0},
                    {"title": "Volume", "value": "250ml", "cost": 500},
                    {"title": "Volume", "value": "500ml", "cost": 900},
                ],
            },
            {
                "name": "Vabysmo",
                "category": "Ophthalmology",
                "price": 20000,
                "specialty": "ophthalmology",
                "description": "Injection solution containing 120 mg of active ingredient",
                "variants": [
                    {"title": "Pack", "value": "Single vial", "cost": 0},
                    {"title": "Pack", "value": "3-pack", "cost": 5000},
                ],
            },
            {
                "name": "Ophthavet",
                "category": "Ophthalmology",
                "price": 2250,
                "specialty": "ophthalmology",
                "description": "Ophthalmic solution for eye care",
                "variants": [
                    {"title": "Volume", "value": "5ml", "cost": 0},
                    {"title": "Volume", "value": "10ml", "cost": 1000},
                ],
            },
            # Orthopedics Products
            {
                "name": "Alvityl Chondroflex",
                "category": "Orthopedics",
                "price": 3250,
                "specialty": "orthopedics",
                "description": "Joint health supplement with chondroitin and glucosamine for maintaining cartilage and joint function",
                "variants": [
                    {"title": "Pack", "value": "30 tablets", "cost": 0},
                    {"title": "Pack", "value": "60 tablets", "cost": 2800},
                    {"title": "Pack", "value": "90 tablets", "cost": 4200},
                ],
            },
            {
                "name": "Structoflex",
                "category": "Orthopedics",
                "price": 4000,
                "specialty": "orthopedics",
                "description": "Joint supplement containing chondroitin sulfate for supporting joint mobility and cartilage health",
                "variants": [
                    {"title": "Form", "value": "Tablets", "cost": 0},
                    {"title": "Form", "value": "Capsules", "cost": 300},
                    {"title": "Pack", "value": "30 count", "cost": 0},
                    {"title": "Pack", "value": "60 count", "cost": 3500},
                ],
            },
            {
                "name": "Salusan Ortho",
                "category": "Orthopedics",
                "price": 2750,
                "specialty": "orthopedics",
                "description": "Orthopedic health supplement with collagen and vitamins to support bones and joints",
                "variants": [
                    {"title": "Pack", "value": "30 sachets", "cost": 0},
                    {"title": "Pack", "value": "60 sachets", "cost": 2400},
                ],
            },
            # Pediatrics Products
            {
                "name": "EfferalganMed Pédiatrique (Paracétamol 30 mg/ml)",
                "category": "Pediatrics",
                "price": 550,
                "specialty": "pediatrics",
                "description": "Pediatric paracetamol solution for pain and fever relief in children aged 4 to 32 kg",
                "variants": [
                    {"title": "Volume", "value": "90ml bottle", "cost": 0},
                    {"title": "Volume", "value": "150ml bottle", "cost": 400},
                ],
            },
            {
                "name": "Melilax",
                "category": "Pediatrics",
                "price": 1600,
                "specialty": "pediatrics",
                "description": "Herbal laxative supplement for gentle relief of occasional constipation",
                "variants": [
                    {
                        "title": "Form",
                        "value": "Pediatric microenemas (6x5g)",
                        "cost": 0,
                    },
                    {
                        "title": "Form",
                        "value": "Adult microenemas (6x10g)",
                        "cost": 500,
                    },
                ],
            },
            {
                "name": "Doliprane (Paracetamol)",
                "category": "Pediatrics",
                "price": 1000,
                "specialty": "pediatrics",
                "description": "Pain reliever and fever reducer containing paracetamol (acetaminophen)",
                "variants": [
                    {"title": "Strength", "value": "100mg suppositories", "cost": 0},
                    {"title": "Strength", "value": "200mg suppositories", "cost": 200},
                    {"title": "Strength", "value": "300mg suppositories", "cost": 300},
                ],
            },
            # Pneumology Products
            {
                "name": "Deslor (Desloratadine 5 mg)",
                "category": "Pneumology",
                "price": 1500,
                "specialty": "general",
                "description": "Antihistamine tablets for allergy relief",
                "variants": [
                    {"title": "Pack", "value": "10 tablets", "cost": 0},
                    {"title": "Pack", "value": "20 tablets", "cost": 1300},
                    {"title": "Pack", "value": "30 tablets", "cost": 1800},
                ],
            },
            {
                "name": "Peak Flow Meter",
                "category": "Pneumology",
                "price": 2250,
                "specialty": "general",
                "description": "Device for measuring respiratory flow rate",
                "variants": [
                    {"title": "Type", "value": "Standard", "cost": 0},
                    {"title": "Type", "value": "Digital", "cost": 1500},
                ],
            },
            {
                "name": "Nebulizer",
                "category": "Pneumology",
                "price": 4500,
                "specialty": "general",
                "description": "Electronic device for administering medication in mist form",
                "variants": [
                    {"title": "Type", "value": "Compressor", "cost": 0},
                    {"title": "Type", "value": "Ultrasonic", "cost": 2000},
                    {"title": "Type", "value": "Mesh", "cost": 3500},
                ],
            },
            # Surgery Products
            {
                "name": "Surgical Instrument Set",
                "category": "Surgery",
                "price": 7500,
                "specialty": "general",
                "description": "Basic set of surgical instruments including forceps, scissors, and scalpel handles",
                "variants": [
                    {"title": "Set", "value": "Minor Surgery (10 pcs)", "cost": 0},
                    {"title": "Set", "value": "General Surgery (25 pcs)", "cost": 5000},
                    {"title": "Set", "value": "Complete (50 pcs)", "cost": 12000},
                ],
            },
            {
                "name": "Disposable Surgical Gloves",
                "category": "Surgery",
                "price": 1750,
                "specialty": "general",
                "description": "Box of sterile latex or nitrile examination gloves",
                "variants": [
                    {"title": "Material", "value": "Latex", "cost": 0},
                    {"title": "Material", "value": "Nitrile", "cost": 300},
                    {"title": "Size", "value": "Small", "cost": 0},
                    {"title": "Size", "value": "Medium", "cost": 0},
                    {"title": "Size", "value": "Large", "cost": 0},
                    {"title": "Size", "value": "X-Large", "cost": 0},
                ],
            },
            {
                "name": "Medical Tape",
                "category": "Surgery",
                "price": 350,
                "specialty": "general",
                "description": "Roll of hypoallergenic medical tape",
                "variants": [
                    {"title": "Width", "value": "1.25cm x 5m", "cost": 0},
                    {"title": "Width", "value": "2.5cm x 5m", "cost": 100},
                    {"title": "Width", "value": "5cm x 5m", "cost": 250},
                ],
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

                # Add product variants
                if "variants" in prod_data:
                    for order, variant_data in enumerate(prod_data["variants"]):
                        ProductVariant.objects.create(
                            product=product,
                            variant_title=variant_data["title"],
                            variant_value=variant_data["value"],
                            additional_cost=Decimal(str(variant_data["cost"])),
                            stock_quantity=random.randint(5, 100),
                            is_active=True,
                            display_order=order,
                        )
                    self.stdout.write(
                        f"  Added {len(prod_data['variants'])} variants for {product.name}"
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

        self.stdout.write(
            self.style.SUCCESS("Successfully seeded products with variants!")
        )
