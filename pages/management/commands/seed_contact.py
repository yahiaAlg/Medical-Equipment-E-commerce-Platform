from django.core.management.base import BaseCommand
from ...models import ContactMessage, FAQ, Testimonial, SiteInformation


class Command(BaseCommand):
    help = (
        "Initialise les messages de contact, FAQ, témoignages et informations du site"
    )

    def handle(self, *args, **kwargs):
        self.stdout.write("Initialisation des données de contact...")

        # Create or update Site Information
        site_info = SiteInformation.get_instance()
        site_info.company_name = "Fennec Med"
        site_info.tva_rate = 0.05
        site_info.tagline = "Fournisseur de matériel médical de qualité aux familles de la région depuis 2022"
        site_info.phone = "03 9591 5378"
        site_info.fax = "03 7068 5073"
        site_info.email = "admin@newbaymedical.com.au"
        site_info.address = "59 Bay St, Brighton VIC 3186"
        site_info.facebook_url = "#"
        site_info.instagram_url = "#"
        site_info.whatsapp_url = "#"
        site_info.youtube_url = "#"
        site_info.about_text = """Nous croyons que l'obtention de fournitures médicales doit être à la fois simple et fiable. 
        Dès que vous nous contactez, vous bénéficiez d'un processus fluide avec une équipe chaleureuse et attentionnée. 
        Notre engagement envers l'excellence signifie que nous évoluons constamment, afin de vous garantir les meilleurs produits 
        et le meilleur service possible."""
        site_info.save()
        self.stdout.write("Informations du site créées/mises à jour")

        # Create FAQs
        faqs_data = [
            {
                "category": "ordering",
                "question": "Comment passer une commande en gros ?",
                "answer": "Vous pouvez passer des commandes en gros directement via notre site web. Ajoutez des produits au panier et les quantités de 10+ bénéficient automatiquement de remises sur les prix en gros. Pour les commandes supérieures à 10 000 $, contactez notre équipe commerciale pour des remises supplémentaires.",
                "order": 1,
            },
            {
                "category": "ordering",
                "question": "Proposez-vous des options de location ?",
                "answer": "Oui, nous proposons des options de location flexibles pour l'achat d'équipements. Contactez notre service de financement pour discuter des conditions et des exigences.",
                "order": 2,
            },
            {
                "category": "shipping",
                "question": "Quels sont vos délais de livraison ?",
                "answer": "La livraison standard prend 5 à 7 jours ouvrables. La livraison express (2-3 jours) et la livraison le lendemain sont disponibles pour les commandes urgentes.",
                "order": 1,
            },
            {
                "category": "shipping",
                "question": "Livrez-vous à l'international ?",
                "answer": "Oui, nous livrons dans la plupart des pays du monde. Les délais de livraison internationale varient selon la destination, généralement 10 à 15 jours ouvrables.",
                "order": 2,
            },
            {
                "category": "technical",
                "question": "Vos produits sont-ils livrés avec un support d'installation ?",
                "answer": "Tous les équipements majeurs incluent des guides d'installation. Des services d'installation professionnelle sont disponibles moyennant des frais supplémentaires.",
                "order": 1,
            },
            {
                "category": "technical",
                "question": "Quel type de formation proposez-vous ?",
                "answer": "Nous proposons des programmes de formation complets incluant des tutoriels en ligne, des formations en présentiel et un support technique continu.",
                "order": 2,
            },
            {
                "category": "warranty",
                "question": "Que couvre la garantie ?",
                "answer": "Notre garantie couvre les défauts de fabrication et les pannes d'équipement dans des conditions d'utilisation normale. Des options de garantie étendue sont disponibles.",
                "order": 1,
            },
            {
                "category": "warranty",
                "question": "Comment faire valoir la garantie ?",
                "answer": "Contactez notre équipe d'assistance avec votre numéro de commande et la description du problème. Nous organiserons une réparation ou un remplacement selon le cas.",
                "order": 2,
            },
            {
                "category": "returns",
                "question": "Quelle est votre politique de retour ?",
                "answer": "Politique de retour de 30 jours sur la plupart des articles. L'équipement doit être inutilisé et dans son emballage d'origine. Les commandes personnalisées ne sont pas remboursables.",
                "order": 1,
            },
            {
                "category": "returns",
                "question": "Comment initier un retour ?",
                "answer": "Contactez le service client pour recevoir un numéro d'autorisation de retour. Renvoyez l'article avec tout l'emballage et la documentation d'origine.",
                "order": 2,
            },
        ]

        for faq_data in faqs_data:
            FAQ.objects.get_or_create(question=faq_data["question"], defaults=faq_data)

        self.stdout.write(f"{len(faqs_data)} FAQ créées")

        # Create Testimonials
        testimonials_data = [
            {
                "name": "Jean Dupont",
                "position": "Client",
                "company": "",
                "content": "Les produits sont de grande qualité et le service est excellent. Je recommande vivement !",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Marie Dubois",
                "position": "Cliente",
                "company": "",
                "content": "Excellente expérience avec Fennec Med. Le personnel est très compétent et serviable.",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Pierre Martin",
                "position": "Client",
                "company": "",
                "content": "J'utilise leurs fournitures médicales depuis des années et j'ai toujours été satisfait.",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Dr Robert Martinez",
                "position": "Chef de cardiologie",
                "company": "Hôpital général métropolitain",
                "content": "Équipement de qualité exceptionnelle et service client exceptionnel. Les outils de diagnostic ont considérablement amélioré nos capacités de soins aux patients.",
                "rating": 5,
                "is_featured": False,
            },
            {
                "name": "Lisa Thompson",
                "position": "Responsable de pharmacie",
                "company": "Chaîne de pharmacies HealthPlus",
                "content": "Nous commandons auprès de ce fournisseur depuis plus de 3 ans. Fiable, prix compétitifs et livraison rapide à chaque fois.",
                "rating": 5,
                "is_featured": False,
            },
        ]

        for test_data in testimonials_data:
            Testimonial.objects.get_or_create(
                name=test_data["name"], defaults=test_data
            )

        self.stdout.write(f"{len(testimonials_data)} témoignages créés")

        # Create sample contact messages
        messages_data = [
            {
                "name": "Jean Bertrand",
                "email": "jean.bertrand@hopital.com",
                "phone": "+33 1 55 01 01 01",
                "inquiry_type": "general",
                "subject": "Intéressé par les tarifs en gros",
                "message": "Nous cherchons à acheter des équipements de diagnostic pour notre nouvelle aile. Pourriez-vous fournir des informations sur les remises en gros ?",
            },
            {
                "name": "Sophie Leroy",
                "email": "sophie.l@clinique.com",
                "phone": "+33 1 55 01 01 02",
                "inquiry_type": "technical",
                "subject": "Question sur l'installation d'équipement",
                "message": "Proposez-vous des services d'installation pour les appareils d'échographie ? Quelles sont les exigences ?",
            },
            {
                "name": "David Moreau",
                "email": "dmoreau@pharmacie.com",
                "inquiry_type": "partnership",
                "subject": "Opportunité de partenariat",
                "message": "Notre chaîne de pharmacies est intéressée par l'établissement d'un partenariat à long terme. Veuillez nous contacter pour en discuter.",
            },
        ]

        for msg_data in messages_data:
            ContactMessage.objects.get_or_create(
                email=msg_data["email"], subject=msg_data["subject"], defaults=msg_data
            )

        self.stdout.write(f"{len(messages_data)} messages de contact créés")
        self.stdout.write(
            self.style.SUCCESS("Données de contact initialisées avec succès !")
        )
