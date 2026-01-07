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

        # Créer les catégories basées sur les pages HTML
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

        # Créer les produits basés sur les pages HTML
        products_data = [
            # Produits de cardiologie
            {
                "name": "Électrodes ECG",
                "categories": ["Cardiologie"],
                "price": 2600,
                "specialty": "cardiology",
                "description": "Électrodes jetables pré-gélifiées pour surveillance cardiaque",
                "variants": [
                    {"title": "Taille du pack", "value": "Pack de 50", "cost": 0},
                    {"title": "Taille du pack", "value": "Pack de 100", "cost": 1500},
                    {"title": "Taille du pack", "value": "Pack de 200", "cost": 2800},
                ],
            },
            {
                "name": "Lancettes de sang",
                "categories": ["Cardiologie", "Laboratoire"],
                "price": 4000,
                "specialty": "cardiology",
                "description": "Lancettes stériles à usage unique pour prélèvement sanguin",
                "variants": [
                    {"title": "Calibre", "value": "28G", "cost": 0},
                    {"title": "Calibre", "value": "30G", "cost": 200},
                    {"title": "Quantité", "value": "100 pcs", "cost": 0},
                    {"title": "Quantité", "value": "200 pcs", "cost": 1800},
                ],
            },
            {
                "name": "CardioAspirine",
                "categories": ["Cardiologie"],
                "price": 200,
                "specialty": "cardiology",
                "description": "Aspirine à faible dose pour la protection cardiovasculaire et l'anticoagulation",
                "variants": [
                    {"title": "Dosage", "value": "75mg", "cost": 0},
                    {"title": "Dosage", "value": "100mg", "cost": 50},
                    {"title": "Taille du pack", "value": "30 comprimés", "cost": 0},
                    {"title": "Taille du pack", "value": "60 comprimés", "cost": 150},
                ],
            },
            # Produits de dentisterie
            {
                "name": "Ledermix",
                "categories": ["Dentisterie"],
                "price": 2000,
                "specialty": "general",
                "description": "Pâte dentaire sur ordonnance contenant acétonide de triamcinolone et chlortétracycline HCl",
                "variants": [
                    {"title": "Taille", "value": "Tube de 5g", "cost": 0},
                    {"title": "Taille", "value": "Tube de 10g", "cost": 800},
                ],
            },
            {
                "name": "Oraqix",
                "categories": ["Dentisterie"],
                "price": 4000,
                "specialty": "general",
                "description": "Gel parodontal contenant lidocaïne et prilocaïne pour anesthésie locale",
                "variants": [
                    {"title": "Volume", "value": "Cartouche de 1,7g", "cost": 0},
                    {"title": "Pack", "value": "Unitaire", "cost": 0},
                    {"title": "Pack", "value": "Boîte de 20", "cost": 15000},
                ],
            },
            {
                "name": "Détartreurs dentaires",
                "categories": ["Dentisterie", "Chirurgie"],
                "price": 3000,
                "specialty": "general",
                "description": "Ensemble d'instruments dentaires pour éliminer la plaque et le tartre des dents",
                "variants": [
                    {
                        "title": "Type d'ensemble",
                        "value": "Basique (3 pièces)",
                        "cost": 0,
                    },
                    {
                        "title": "Type d'ensemble",
                        "value": "Professionnel (6 pièces)",
                        "cost": 2000,
                    },
                    {
                        "title": "Type d'ensemble",
                        "value": "Complet (12 pièces)",
                        "cost": 4500,
                    },
                ],
            },
            # Produits de dermatologie
            {
                "name": "Canestene DERM",
                "categories": ["Dermatologie"],
                "price": 1150,
                "specialty": "dermatology",
                "description": "Crème antifongique pour traiter les infections cutanées comme le pied d'athlète, la teigne et les irritations cutanées fongiques",
                "variants": [
                    {"title": "Taille", "value": "15g", "cost": 0},
                    {"title": "Taille", "value": "30g", "cost": 600},
                    {"title": "Taille", "value": "50g", "cost": 1000},
                ],
            },
            {
                "name": "Dermo Cuivre",
                "categories": ["Dermatologie"],
                "price": 1400,
                "specialty": "dermatology",
                "description": "Pommade réparatrice pour traiter les plaies mineures, brûlures et irritations cutanées",
                "variants": [
                    {"title": "Volume", "value": "20ml", "cost": 0},
                    {"title": "Volume", "value": "50ml", "cost": 800},
                ],
            },
            {
                "name": "Biafine",
                "categories": ["Dermatologie"],
                "price": 1700,
                "specialty": "dermatology",
                "description": "Crème de soins cutanés apaisante et protectrice pour peaux irritées ou abîmées",
                "variants": [
                    {"title": "Taille", "value": "Tube de 93g", "cost": 0},
                    {"title": "Taille", "value": "Tube de 186g", "cost": 1500},
                ],
            },
            # Produits de gastro-entérologie
            {
                "name": "Spascol LP",
                "categories": ["Gastro-entérologie"],
                "price": 1150,
                "specialty": "general",
                "description": "Médicament myorelaxant pour traiter les spasmes musculaires et la douleur",
                "variants": [
                    {"title": "Taille du pack", "value": "20 comprimés", "cost": 0},
                    {"title": "Taille du pack", "value": "40 comprimés", "cost": 900},
                ],
            },
            {
                "name": "Gastricalm",
                "categories": ["Gastro-entérologie"],
                "price": 850,
                "specialty": "general",
                "description": "Médicament pour traiter l'acidité gastrique et les brûlures d'estomac",
                "variants": [
                    {"title": "Forme", "value": "Comprimés", "cost": 0},
                    {"title": "Forme", "value": "Suspension", "cost": 200},
                ],
            },
            {
                "name": "Modèle anatomique d'estomac",
                "categories": ["Gastro-entérologie"],
                "price": 4500,
                "specialty": "general",
                "description": "Modèle pédagogique de l'estomac humain",
                "variants": [
                    {"title": "Taille", "value": "Standard", "cost": 0},
                    {"title": "Taille", "value": "Grand (Enseignement)", "cost": 2000},
                ],
            },
            # Produits de gynécologie
            {
                "name": "Femaferrin",
                "categories": ["Gynécologie"],
                "price": 2000,
                "specialty": "general",
                "description": "Comprimés de supplément de fer pour traiter la carence en fer",
                "variants": [
                    {"title": "Pack", "value": "30 comprimés", "cost": 0},
                    {"title": "Pack", "value": "60 comprimés", "cost": 1700},
                    {"title": "Pack", "value": "90 comprimés", "cost": 2400},
                ],
            },
            {
                "name": "Poignée d'aspiration de qualité avec bouteille",
                "categories": ["Gynécologie", "Chirurgie"],
                "price": 3000,
                "specialty": "general",
                "description": "Dispositif d'aspiration manuel avec bouteille de collecte",
                "variants": [
                    {"title": "Taille de bouteille", "value": "500ml", "cost": 0},
                    {"title": "Taille de bouteille", "value": "1000ml", "cost": 800},
                ],
            },
            {
                "name": "Modèle anatomique (Système reproducteur féminin)",
                "categories": ["Gynécologie"],
                "price": 4500,
                "specialty": "general",
                "description": "Modèle pédagogique de l'anatomie reproductive féminine",
                "variants": [
                    {"title": "Type", "value": "Standard", "cost": 0},
                    {
                        "title": "Type",
                        "value": "Détaillé (avec pathologies)",
                        "cost": 2500,
                    },
                ],
            },
            # Produits de laboratoire
            {
                "name": "Tubes microcentrifuge (1,5 ml)",
                "categories": ["Laboratoire"],
                "price": 3000,
                "specialty": "general",
                "description": "Rack de 96 tubes microcentrifuge à bouchon bleu",
                "variants": [
                    {"title": "Quantité", "value": "96 tubes (1 rack)", "cost": 0},
                    {"title": "Quantité", "value": "480 tubes (5 racks)", "cost": 2500},
                    {"title": "Couleur", "value": "Bleu", "cost": 0},
                    {"title": "Couleur", "value": "Transparent", "cost": 0},
                    {"title": "Couleur", "value": "Assortis", "cost": 200},
                ],
            },
            {
                "name": "Ensemble de verrerie de laboratoire",
                "categories": ["Laboratoire"],
                "price": 2250,
                "specialty": "general",
                "description": "Ensemble comprenant bécher, éprouvette graduée et fiole Erlenmeyer",
                "variants": [
                    {"title": "Ensemble", "value": "Basique (3 pièces)", "cost": 0},
                    {"title": "Ensemble", "value": "Standard (6 pièces)", "cost": 1500},
                    {
                        "title": "Ensemble",
                        "value": "Professionnel (12 pièces)",
                        "cost": 3000,
                    },
                ],
            },
            {
                "name": "Pissette (500 ml)",
                "categories": ["Laboratoire"],
                "price": 550,
                "specialty": "general",
                "description": "Pissette en plastique avec embout presseur",
                "variants": [
                    {"title": "Volume", "value": "250ml", "cost": -200},
                    {"title": "Volume", "value": "500ml", "cost": 0},
                    {"title": "Volume", "value": "1000ml", "cost": 300},
                ],
            },
            # Produits de neurologie
            {
                "name": "Marteau à réflexes",
                "categories": ["Neurologie"],
                "price": 2000,
                "specialty": "neurology",
                "description": "Outil pour tester les réflexes du patient",
                "variants": [
                    {"title": "Type", "value": "Taylor", "cost": 0},
                    {"title": "Type", "value": "Buck", "cost": 300},
                    {"title": "Type", "value": "Babinski", "cost": 500},
                ],
            },
            {
                "name": "Plateau de ponction lombaire",
                "categories": ["Neurologie", "Chirurgie"],
                "price": 20000,
                "specialty": "neurology",
                "description": "Kit stérile pour effectuer des ponctions rachidiennes et analyses du liquide céphalorachidien",
                "variants": [
                    {"title": "Taille d'aiguille", "value": "20G", "cost": 0},
                    {"title": "Taille d'aiguille", "value": "22G", "cost": 500},
                    {"title": "Taille d'aiguille", "value": "25G", "cost": 1000},
                ],
            },
            {
                "name": "Neurobion Forte",
                "categories": ["Neurologie"],
                "price": 1500,
                "specialty": "neurology",
                "description": "Supplément de complexe vitaminique B qui aide à soulager les picotements, engourdissements et faiblesses",
                "variants": [
                    {"title": "Pack", "value": "30 comprimés", "cost": 0},
                    {"title": "Pack", "value": "60 comprimés", "cost": 1300},
                ],
            },
            # Produits d'ophtalmologie
            {
                "name": "Vibac",
                "categories": ["Ophtalmologie", "Chirurgie"],
                "price": 750,
                "specialty": "ophthalmology",
                "description": "Solution antiseptique pour désinfection cutanée",
                "variants": [
                    {"title": "Volume", "value": "100ml", "cost": 0},
                    {"title": "Volume", "value": "250ml", "cost": 500},
                    {"title": "Volume", "value": "500ml", "cost": 900},
                ],
            },
            {
                "name": "Vabysmo",
                "categories": ["Ophtalmologie"],
                "price": 20000,
                "specialty": "ophthalmology",
                "description": "Solution injectable contenant 120 mg de principe actif",
                "variants": [
                    {"title": "Pack", "value": "Flacon unique", "cost": 0},
                    {"title": "Pack", "value": "Pack de 3", "cost": 5000},
                ],
            },
            {
                "name": "Ophthavet",
                "categories": ["Ophtalmologie"],
                "price": 2250,
                "specialty": "ophthalmology",
                "description": "Solution ophtalmique pour soins oculaires",
                "variants": [
                    {"title": "Volume", "value": "5ml", "cost": 0},
                    {"title": "Volume", "value": "10ml", "cost": 1000},
                ],
            },
            # Produits d'orthopédie
            {
                "name": "Alvityl Chondroflex",
                "categories": ["Orthopédie"],
                "price": 3250,
                "specialty": "orthopedics",
                "description": "Supplément pour la santé articulaire avec chondroïtine et glucosamine pour maintenir le cartilage et la fonction articulaire",
                "variants": [
                    {"title": "Pack", "value": "30 comprimés", "cost": 0},
                    {"title": "Pack", "value": "60 comprimés", "cost": 2800},
                    {"title": "Pack", "value": "90 comprimés", "cost": 4200},
                ],
            },
            {
                "name": "Structoflex",
                "categories": ["Orthopédie"],
                "price": 4000,
                "specialty": "orthopedics",
                "description": "Supplément articulaire contenant du sulfate de chondroïtine pour soutenir la mobilité articulaire et la santé du cartilage",
                "variants": [
                    {"title": "Forme", "value": "Comprimés", "cost": 0},
                    {"title": "Forme", "value": "Capsules", "cost": 300},
                    {"title": "Pack", "value": "30 unités", "cost": 0},
                    {"title": "Pack", "value": "60 unités", "cost": 3500},
                ],
            },
            {
                "name": "Salusan Ortho",
                "categories": ["Orthopédie"],
                "price": 2750,
                "specialty": "orthopedics",
                "description": "Supplément pour la santé orthopédique avec collagène et vitamines pour soutenir les os et les articulations",
                "variants": [
                    {"title": "Pack", "value": "30 sachets", "cost": 0},
                    {"title": "Pack", "value": "60 sachets", "cost": 2400},
                ],
            },
            # Produits de pédiatrie
            {
                "name": "EfferalganMed Pédiatrique (Paracétamol 30 mg/ml)",
                "categories": ["Pédiatrie"],
                "price": 550,
                "specialty": "pediatrics",
                "description": "Solution pédiatrique de paracétamol pour soulager la douleur et la fièvre chez les enfants de 4 à 32 kg",
                "variants": [
                    {"title": "Volume", "value": "Flacon de 90ml", "cost": 0},
                    {"title": "Volume", "value": "Flacon de 150ml", "cost": 400},
                ],
            },
            {
                "name": "Melilax",
                "categories": ["Pédiatrie"],
                "price": 1600,
                "specialty": "pediatrics",
                "description": "Supplément laxatif à base de plantes pour un soulagement doux de la constipation occasionnelle",
                "variants": [
                    {
                        "title": "Forme",
                        "value": "Microlavements pédiatriques (6x5g)",
                        "cost": 0,
                    },
                    {
                        "title": "Forme",
                        "value": "Microlavements adultes (6x10g)",
                        "cost": 500,
                    },
                ],
            },
            {
                "name": "Doliprane (Paracétamol)",
                "categories": ["Pédiatrie"],
                "price": 1000,
                "specialty": "pediatrics",
                "description": "Analgésique et antipyrétique contenant du paracétamol (acétaminophène)",
                "variants": [
                    {"title": "Dosage", "value": "Suppositoires 100mg", "cost": 0},
                    {"title": "Dosage", "value": "Suppositoires 200mg", "cost": 200},
                    {"title": "Dosage", "value": "Suppositoires 300mg", "cost": 300},
                ],
            },
            # Produits de pneumologie
            {
                "name": "Deslor (Desloratadine 5 mg)",
                "categories": ["Pneumologie"],
                "price": 1500,
                "specialty": "general",
                "description": "Comprimés antihistaminiques pour le soulagement des allergies",
                "variants": [
                    {"title": "Pack", "value": "10 comprimés", "cost": 0},
                    {"title": "Pack", "value": "20 comprimés", "cost": 1300},
                    {"title": "Pack", "value": "30 comprimés", "cost": 1800},
                ],
            },
            {
                "name": "Débitmètre de pointe",
                "categories": ["Pneumologie"],
                "price": 2250,
                "specialty": "general",
                "description": "Appareil pour mesurer le débit respiratoire",
                "variants": [
                    {"title": "Type", "value": "Standard", "cost": 0},
                    {"title": "Type", "value": "Numérique", "cost": 1500},
                ],
            },
            {
                "name": "Nébuliseur",
                "categories": ["Pneumologie", "Pédiatrie"],
                "price": 4500,
                "specialty": "general",
                "description": "Appareil électronique pour administrer des médicaments sous forme de brouillard",
                "variants": [
                    {"title": "Type", "value": "Compresseur", "cost": 0},
                    {"title": "Type", "value": "Ultrasonique", "cost": 2000},
                    {"title": "Type", "value": "Maille", "cost": 3500},
                ],
            },
            # Produits de chirurgie
            {
                "name": "Ensemble d'instruments chirurgicaux",
                "categories": ["Chirurgie"],
                "price": 7500,
                "specialty": "general",
                "description": "Ensemble de base d'instruments chirurgicaux comprenant pinces, ciseaux et manches de scalpel",
                "variants": [
                    {
                        "title": "Ensemble",
                        "value": "Chirurgie mineure (10 pcs)",
                        "cost": 0,
                    },
                    {
                        "title": "Ensemble",
                        "value": "Chirurgie générale (25 pcs)",
                        "cost": 5000,
                    },
                    {"title": "Ensemble", "value": "Complet (50 pcs)", "cost": 12000},
                ],
            },
            {
                "name": "Gants chirurgicaux jetables",
                "categories": ["Chirurgie", "Laboratoire"],
                "price": 1750,
                "specialty": "general",
                "description": "Boîte de gants d'examen stériles en latex ou nitrile",
                "variants": [
                    {"title": "Matériau", "value": "Latex", "cost": 0},
                    {"title": "Matériau", "value": "Nitrile", "cost": 300},
                    {"title": "Taille", "value": "Petit", "cost": 0},
                    {"title": "Taille", "value": "Moyen", "cost": 0},
                    {"title": "Taille", "value": "Grand", "cost": 0},
                    {"title": "Taille", "value": "Très grand", "cost": 0},
                ],
            },
            {
                "name": "Ruban médical",
                "categories": ["Chirurgie"],
                "price": 350,
                "specialty": "general",
                "description": "Rouleau de ruban médical hypoallergénique",
                "variants": [
                    {"title": "Largeur", "value": "1,25cm x 5m", "cost": 0},
                    {"title": "Largeur", "value": "2,5cm x 5m", "cost": 100},
                    {"title": "Largeur", "value": "5cm x 5m", "cost": 250},
                ],
            },
        ]

        for idx, prod_data in enumerate(products_data):
            product, created = Product.objects.get_or_create(
                name=prod_data["name"],
                defaults={
                    "brand": random.choice(brands),
                    "price": Decimal(str(prod_data["price"])),
                    "bulk_price": Decimal(str(prod_data["price"] * 0.85)),
                    "bulk_quantity": 10,
                    "sku": f"FEN-{1000 + idx}",
                    "stock_quantity": random.randint(10, 150),
                    "specialty": prod_data["specialty"],
                    "availability_status": "in_stock",
                    "short_description": prod_data["description"],
                    "description": f'{prod_data["description"]}. Qualité professionnelle pour usage médical. Conforme à toutes les normes et réglementations médicales.',
                    "specifications": "Qualité médicale professionnelle\nGarantie : 1-2 ans\nCertifications : Conforme aux normes médicales",
                    "warranty": "Garantie constructeur standard",
                    "featured": random.choice([True, False]),
                    "trending": random.choice([True, False]),
                },
            )

            if created:
                self.stdout.write(f"Produit créé : {product.name}")

                # Ajouter les catégories (relation M2M)
                for cat_name in prod_data["categories"]:
                    product.categories.add(categories[cat_name])
                self.stdout.write(
                    f"  Catégories ajoutées : {', '.join(prod_data['categories'])}"
                )

                # Ajouter des images de placeholder
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

                # Ajouter les variantes de produits
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
                        f"  {len(prod_data['variants'])} variantes ajoutées pour {product.name}"
                    )

        # Créer des avis d'exemple
        users = User.objects.all()
        if users.exists():
            products = Product.objects.all()[:15]
            review_titles = [
                "Excellente qualité",
                "Très bon produit",
                "Hautement recommandé",
                "Parfait pour notre clinique",
                "Équipement de qualité professionnelle",
                "Très satisfait",
                "Bon rapport qualité-prix",
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

        self.stdout.write(
            self.style.SUCCESS("Produits avec variantes générés avec succès !")
        )
