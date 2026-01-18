from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from ...models import (
    Category,
    Brand,
    BulkContainerType,
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
    help = "Génère les produits, catégories, marques, images et variantes"

    def download_image(self, url):
        """Télécharge une image depuis une URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content)
        except:
            pass
        return None

    def handle(self, *args, **kwargs):
        self.stdout.write("Génération des produits...")

        # Créer les types de conteneurs en gros
        container_types_data = [
            {
                "name": "Carton",
                "description": "Carton standard pour produits médicaux",
                "typical_capacity": "20-100 unités",
            },
            {
                "name": "Réservoir",
                "description": "Réservoir pour liquides en vrac",
                "typical_capacity": "5-50 litres",
            },
            {
                "name": "Colis",
                "description": "Colis postal ou logistique",
                "typical_capacity": "10-50 unités",
            },
            {
                "name": "Boîte",
                "description": "Boîte de rangement",
                "typical_capacity": "5-30 unités",
            },
            {
                "name": "Palette",
                "description": "Palette de transport",
                "typical_capacity": "100-500 unités",
            },
            {
                "name": "Sac",
                "description": "Sac en plastique ou papier",
                "typical_capacity": "10-100 unités",
            },
            {
                "name": "Fût",
                "description": "Fût ou baril pour stockage",
                "typical_capacity": "10-200 litres",
            },
            {
                "name": "Conteneur",
                "description": "Conteneur de grande capacité",
                "typical_capacity": "500-5000 unités",
            },
        ]

        container_types = {}
        for ct_data in container_types_data:
            ct, created = BulkContainerType.objects.get_or_create(
                name=ct_data["name"],
                defaults={
                    "description": ct_data["description"],
                    "typical_capacity": ct_data["typical_capacity"],
                },
            )
            container_types[ct_data["name"]] = ct
            if created:
                self.stdout.write(f"Type de conteneur créé : {ct.name}")

        # Créer les catégories
        categories_data = [
            {
                "name": "Cardiologie",
                "description": "Équipements et fournitures de soins cardiovasculaires",
            },
            {
                "name": "Neurologie",
                "description": "Équipements de diagnostic et de traitement neurologiques",
            },
            {
                "name": "Orthopédie",
                "description": "Équipements de soins des os, articulations et muscles",
            },
            {
                "name": "Pédiatrie",
                "description": "Équipements spécialisés pour enfants et adolescents",
            },
            {
                "name": "Dermatologie",
                "description": "Équipements de soins de la peau, cheveux et ongles",
            },
            {
                "name": "Ophtalmologie",
                "description": "Équipements de soins oculaires et de vision",
            },
            {
                "name": "Chirurgie",
                "description": "Instruments et équipements chirurgicaux",
            },
            {
                "name": "Gastro-entérologie",
                "description": "Équipements de diagnostic et traitement du système digestif",
            },
            {
                "name": "Laboratoire",
                "description": "Équipements de tests diagnostiques et d'analyse",
            },
            {
                "name": "Gynécologie",
                "description": "Équipements de santé féminine et de soins reproductifs",
            },
            {
                "name": "Pneumologie",
                "description": "Équipements pour les maladies respiratoires et pulmonaires",
            },
            {
                "name": "Dentisterie",
                "description": "Équipements de soins dentaires et de santé bucco-dentaire",
            },
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"], defaults={"description": cat_data["description"]}
            )
            categories[cat_data["name"]] = cat
            if created:
                self.stdout.write(f"Catégorie créée : {cat.name}")

        # Créer les marques
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
                defaults={"description": f"Fabricant leader d'équipements médicaux"},
            )
            brands.append(brand)

        # Créer les produits avec nouvelles variantes
        products_data = [
            # Produits de cardiologie
            {
                "name": "Électrodes ECG",
                "categories": ["Cardiologie"],
                "specialty": "cardiology",
                "description": "Électrodes jetables pré-gélifiées pour surveillance cardiaque",
                "variants": [
                    {
                        "title": "Pack standard",
                        "value": "50 unités",
                        "type": "retail",
                        "price": 2600,
                    },
                    {
                        "title": "Pack moyen",
                        "value": "100 unités",
                        "type": "retail",
                        "price": 4100,
                    },
                    {
                        "title": "Carton",
                        "value": "200 unités",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 200,
                        "unit_price": 22,
                        "wholesale": 3800,
                    },
                ],
            },
            {
                "name": "Lancettes de sang",
                "categories": ["Cardiologie", "Laboratoire"],
                "specialty": "cardiology",
                "description": "Lancettes stériles à usage unique pour prélèvement sanguin",
                "variants": [
                    {
                        "title": "28G",
                        "value": "100 pcs",
                        "type": "retail",
                        "price": 4000,
                    },
                    {
                        "title": "30G",
                        "value": "100 pcs",
                        "type": "retail",
                        "price": 4200,
                    },
                    {
                        "title": "Boîte 28G",
                        "value": "500 pcs",
                        "type": "bulk",
                        "container": "Boîte",
                        "units": 500,
                        "unit_price": 38,
                        "wholesale": 17000,
                    },
                ],
            },
            {
                "name": "CardioAspirine",
                "categories": ["Cardiologie"],
                "specialty": "cardiology",
                "description": "Aspirine à faible dose pour la protection cardiovasculaire",
                "variants": [
                    {
                        "title": "75mg",
                        "value": "30 comprimés",
                        "type": "retail",
                        "price": 200,
                    },
                    {
                        "title": "100mg",
                        "value": "30 comprimés",
                        "type": "retail",
                        "price": 250,
                    },
                    {
                        "title": "75mg",
                        "value": "60 comprimés",
                        "type": "retail",
                        "price": 350,
                    },
                ],
            },
            # Produits de dentisterie
            {
                "name": "Ledermix",
                "categories": ["Dentisterie"],
                "specialty": "general",
                "description": "Pâte dentaire sur ordonnance",
                "variants": [
                    {
                        "title": "Petit",
                        "value": "Tube de 5g",
                        "type": "retail",
                        "price": 2000,
                    },
                    {
                        "title": "Grand",
                        "value": "Tube de 10g",
                        "type": "retail",
                        "price": 2800,
                    },
                    {
                        "title": "Carton 5g",
                        "value": "20 tubes",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 20,
                        "unit_price": 1900,
                        "wholesale": 35000,
                    },
                ],
            },
            {
                "name": "Détartreurs dentaires",
                "categories": ["Dentisterie", "Chirurgie"],
                "specialty": "general",
                "description": "Ensemble d'instruments dentaires pour éliminer la plaque",
                "variants": [
                    {
                        "title": "Basique",
                        "value": "3 pièces",
                        "type": "retail",
                        "price": 3000,
                    },
                    {
                        "title": "Professionnel",
                        "value": "6 pièces",
                        "type": "retail",
                        "price": 5000,
                    },
                    {
                        "title": "Complet",
                        "value": "12 pièces",
                        "type": "retail",
                        "price": 7500,
                    },
                ],
            },
            # Produits de dermatologie
            {
                "name": "Canestene DERM",
                "categories": ["Dermatologie"],
                "specialty": "dermatology",
                "description": "Crème antifongique pour traiter les infections cutanées",
                "variants": [
                    {"title": "Petit", "value": "15g", "type": "retail", "price": 1150},
                    {"title": "Moyen", "value": "30g", "type": "retail", "price": 1750},
                    {"title": "Grand", "value": "50g", "type": "retail", "price": 2150},
                    {
                        "title": "Boîte 15g",
                        "value": "12 tubes",
                        "type": "bulk",
                        "container": "Boîte",
                        "units": 12,
                        "unit_price": 1100,
                        "wholesale": 12500,
                    },
                ],
            },
            {
                "name": "Biafine",
                "categories": ["Dermatologie"],
                "specialty": "dermatology",
                "description": "Crème de soins cutanés apaisante et protectrice",
                "variants": [
                    {
                        "title": "Standard",
                        "value": "93g",
                        "type": "retail",
                        "price": 1700,
                    },
                    {
                        "title": "Grande",
                        "value": "186g",
                        "type": "retail",
                        "price": 3200,
                    },
                ],
            },
            # Produits de laboratoire
            {
                "name": "Tubes microcentrifuge (1,5 ml)",
                "categories": ["Laboratoire"],
                "specialty": "general",
                "description": "Tubes microcentrifuge à bouchon",
                "variants": [
                    {
                        "title": "Rack bleu",
                        "value": "96 tubes",
                        "type": "retail",
                        "price": 3000,
                    },
                    {
                        "title": "Carton bleu",
                        "value": "480 tubes",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 480,
                        "unit_price": 30,
                        "wholesale": 13000,
                    },
                    {
                        "title": "Palette mixte",
                        "value": "2400 tubes",
                        "type": "bulk",
                        "container": "Palette",
                        "units": 2400,
                        "unit_price": 27,
                        "wholesale": 60000,
                    },
                ],
            },
            {
                "name": "Gants chirurgicaux jetables",
                "categories": ["Chirurgie", "Laboratoire"],
                "specialty": "general",
                "description": "Boîte de gants d'examen stériles",
                "variants": [
                    {
                        "title": "Latex M",
                        "value": "100 pcs",
                        "type": "retail",
                        "price": 1750,
                    },
                    {
                        "title": "Nitrile M",
                        "value": "100 pcs",
                        "type": "retail",
                        "price": 2050,
                    },
                    {
                        "title": "Carton Latex",
                        "value": "1000 pcs",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 1000,
                        "unit_price": 16,
                        "wholesale": 15000,
                    },
                    {
                        "title": "Carton Nitrile",
                        "value": "1000 pcs",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 1000,
                        "unit_price": 19,
                        "wholesale": 18000,
                    },
                ],
            },
            # Produits de neurologie
            {
                "name": "Marteau à réflexes",
                "categories": ["Neurologie"],
                "specialty": "neurology",
                "description": "Outil pour tester les réflexes du patient",
                "variants": [
                    {
                        "title": "Taylor",
                        "value": "Standard",
                        "type": "retail",
                        "price": 2000,
                    },
                    {
                        "title": "Buck",
                        "value": "Standard",
                        "type": "retail",
                        "price": 2300,
                    },
                    {
                        "title": "Babinski",
                        "value": "Standard",
                        "type": "retail",
                        "price": 2500,
                    },
                ],
            },
            {
                "name": "Neurobion Forte",
                "categories": ["Neurologie"],
                "specialty": "neurology",
                "description": "Supplément de complexe vitaminique B",
                "variants": [
                    {
                        "title": "Standard",
                        "value": "30 comprimés",
                        "type": "retail",
                        "price": 1500,
                    },
                    {
                        "title": "Double",
                        "value": "60 comprimés",
                        "type": "retail",
                        "price": 2800,
                    },
                    {
                        "title": "Carton",
                        "value": "10 boîtes x 30",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 10,
                        "unit_price": 1450,
                        "wholesale": 13500,
                    },
                ],
            },
            # Produits d'ophtalmologie
            {
                "name": "Vibac",
                "categories": ["Ophtalmologie", "Chirurgie"],
                "specialty": "ophthalmology",
                "description": "Solution antiseptique pour désinfection cutanée",
                "variants": [
                    {
                        "title": "Petit",
                        "value": "100ml",
                        "type": "retail",
                        "price": 750,
                    },
                    {
                        "title": "Moyen",
                        "value": "250ml",
                        "type": "retail",
                        "price": 1250,
                    },
                    {
                        "title": "Grand",
                        "value": "500ml",
                        "type": "retail",
                        "price": 1650,
                    },
                    {
                        "title": "Carton 250ml",
                        "value": "12 flacons",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 12,
                        "unit_price": 1200,
                        "wholesale": 13500,
                    },
                ],
            },
            # Produits d'orthopédie
            {
                "name": "Alvityl Chondroflex",
                "categories": ["Orthopédie"],
                "specialty": "orthopedics",
                "description": "Supplément pour la santé articulaire",
                "variants": [
                    {
                        "title": "30 jours",
                        "value": "30 comprimés",
                        "type": "retail",
                        "price": 3250,
                    },
                    {
                        "title": "60 jours",
                        "value": "60 comprimés",
                        "type": "retail",
                        "price": 6050,
                    },
                    {
                        "title": "90 jours",
                        "value": "90 comprimés",
                        "type": "retail",
                        "price": 7450,
                    },
                ],
            },
            # Produits de pédiatrie
            {
                "name": "EfferalganMed Pédiatrique",
                "categories": ["Pédiatrie"],
                "specialty": "pediatrics",
                "description": "Solution pédiatrique de paracétamol",
                "variants": [
                    {
                        "title": "Standard",
                        "value": "90ml",
                        "type": "retail",
                        "price": 550,
                    },
                    {
                        "title": "Grand",
                        "value": "150ml",
                        "type": "retail",
                        "price": 950,
                    },
                    {
                        "title": "Carton 90ml",
                        "value": "12 flacons",
                        "type": "bulk",
                        "container": "Carton",
                        "units": 12,
                        "unit_price": 520,
                        "wholesale": 5900,
                    },
                ],
            },
            {
                "name": "Doliprane",
                "categories": ["Pédiatrie"],
                "specialty": "pediatrics",
                "description": "Analgésique et antipyrétique",
                "variants": [
                    {
                        "title": "100mg",
                        "value": "10 suppositoires",
                        "type": "retail",
                        "price": 1000,
                    },
                    {
                        "title": "200mg",
                        "value": "10 suppositoires",
                        "type": "retail",
                        "price": 1200,
                    },
                    {
                        "title": "300mg",
                        "value": "10 suppositoires",
                        "type": "retail",
                        "price": 1300,
                    },
                ],
            },
            # Produits de pneumologie
            {
                "name": "Nébuliseur",
                "categories": ["Pneumologie", "Pédiatrie"],
                "specialty": "general",
                "description": "Appareil électronique pour administrer des médicaments",
                "variants": [
                    {
                        "title": "Compresseur",
                        "value": "Standard",
                        "type": "retail",
                        "price": 4500,
                    },
                    {
                        "title": "Ultrasonique",
                        "value": "Standard",
                        "type": "retail",
                        "price": 6500,
                    },
                    {
                        "title": "Maille",
                        "value": "Portable",
                        "type": "retail",
                        "price": 8000,
                    },
                ],
            },
        ]

        for idx, prod_data in enumerate(products_data):
            product, created = Product.objects.get_or_create(
                name=prod_data["name"],
                defaults={
                    "brand": random.choice(brands),
                    "price": Decimal("0"),  # Price is 0, comes from variants
                    "sku": f"FEN-{1000 + idx}",
                    "stock_quantity": random.randint(10, 150),
                    "specialty": prod_data["specialty"],
                    "availability_status": "in_stock",
                    "short_description": prod_data["description"],
                    "description": f'{prod_data["description"]}. Qualité professionnelle pour usage médical.',
                    "specifications": "Qualité médicale professionnelle\nGarantie : 1-2 ans",
                    "warranty": "Garantie constructeur standard",
                    "featured": random.choice([True, False]),
                    "trending": random.choice([True, False]),
                },
            )

            if created:
                self.stdout.write(f"Produit créé : {product.name}")

                # Ajouter les catégories
                for cat_name in prod_data["categories"]:
                    product.categories.add(categories[cat_name])

                # Ajouter des images
                for img_num in range(3):
                    image_url = f"https://source.unsplash.com/800x600/?medical,{prod_data['categories'][0].lower()}&sig={idx}{img_num}"
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

                # Ajouter les variantes
                if "variants" in prod_data:
                    for order, v_data in enumerate(prod_data["variants"]):
                        if v_data["type"] == "retail":
                            ProductVariant.objects.create(
                                product=product,
                                variant_title=v_data["title"],
                                variant_value=v_data["value"],
                                purchase_type="retail",
                                retail_price=Decimal(str(v_data["price"])),
                                stock_quantity=random.randint(5, 100),
                                is_active=True,
                                display_order=order,
                            )
                        else:  # bulk
                            ProductVariant.objects.create(
                                product=product,
                                variant_title=v_data["title"],
                                variant_value=v_data["value"],
                                purchase_type="bulk",
                                bulk_container_type=container_types[
                                    v_data["container"]
                                ],
                                units_per_container=v_data["units"],
                                unit_price=Decimal(str(v_data["unit_price"])),
                                wholesale_price=Decimal(str(v_data["wholesale"])),
                                stock_quantity=random.randint(5, 50),
                                is_active=True,
                                display_order=order,
                            )
                    self.stdout.write(
                        f"  {len(prod_data['variants'])} variantes ajoutées"
                    )

        # Créer des avis
        users = User.objects.all()
        if users.exists():
            products = Product.objects.all()[:15]
            review_titles = [
                "Excellente qualité",
                "Très bon produit",
                "Hautement recommandé",
                "Parfait pour notre clinique",
                "Très satisfait",
            ]

            for product in products:
                user = random.choice(users)
                ProductReview.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults={
                        "rating": random.randint(4, 5),
                        "title": random.choice(review_titles),
                        "comment": "Très satisfait de cet achat. Haute qualité et fiable.",
                        "verified_purchase": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Produits générés avec succès !"))
