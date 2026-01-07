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
        site_info.site_name = "Fennec Med"
        site_info.tagline = (
            "Votre partenaire de confiance en équipements médicaux en Algérie"
        )
        site_info.description = "Fennec Med est votre fournisseur de confiance en équipements et fournitures médicales de haute qualité à Sétif et dans toute l'Algérie."
        site_info.tva_rate = 0.19
        site_info.phone = "+213 36 72 45 89"
        site_info.fax = "+213 36 72 45 90"
        site_info.email = "contact@fennecmed.dz"
        site_info.address = "Boulevard de l'ALN, Cité El Hidhab, Sétif 19000, Algérie"

        # Home page content
        site_info.hero_title = "Bienvenue chez Fennec Med"
        site_info.hero_subtitle = "Fournisseur d'équipements médicaux de qualité supérieure aux professionnels de santé et aux particuliers depuis 2022."
        site_info.about_section_title = "À Propos de Fennec Med Sétif"
        site_info.find_us_content = """<p>
            Vous recherchez un fournisseur fiable d'équipements médicaux à Sétif ? Fennec Med est situé 
            au cœur de la ville, desservant les professionnels de santé et les particuliers dans toute 
            la région des Hauts Plateaux. Nous offrons nos services à Sétif, Batna, Bordj Bou Arreridj, 
            M'Sila, et toute la région Est de l'Algérie. Notre engagement est de fournir des équipements 
            médicaux certifiés aux meilleurs prix avec un service après-vente exceptionnel.
        </p>"""
        site_info.cta_title = "Prêt à Équiper Votre Cabinet ?"
        site_info.cta_description = "Contactez-nous dès aujourd'hui pour découvrir notre large gamme d'équipements médicaux certifiés et nos solutions personnalisées."

        # About page content
        site_info.about_hero_title = (
            "Équipements Médicaux de Qualité en Qui Vous Pouvez Avoir Confiance"
        )
        site_info.about_hero_description = """<p>
            Chez Fennec Med, nous comprenons l'importance d'équipements médicaux fiables et performants 
            pour la qualité des soins. Depuis notre établissement en 2022, nous nous sommes engagés à 
            fournir aux professionnels de santé algériens des équipements de classe mondiale, certifiés 
            CE et conformes aux normes internationales. Notre équipe d'experts est là pour vous conseiller 
            et vous accompagner dans le choix des meilleures solutions pour vos besoins.
        </p>"""
        site_info.about_story_title = "Notre Histoire"
        site_info.about_story_content = """<p>
            Fennec Med a été fondée en 2022 avec une vision claire : démocratiser l'accès aux équipements 
            médicaux de qualité en Algérie. Basés à Sétif, nous avons rapidement étendu notre réseau de 
            distribution pour couvrir toute la région Est du pays. Notre catalogue comprend plus de 500 
            produits soigneusement sélectionnés auprès des meilleurs fabricants internationaux.
        </p>
        <p>
            Aujourd'hui, nous sommes fiers de servir des centaines de cliniques, cabinets médicaux, 
            pharmacies et hôpitaux à travers l'Algérie. Notre engagement envers l'excellence nous pousse 
            à constamment élargir notre gamme de produits et améliorer nos services pour mieux répondre 
            aux besoins évolutifs du secteur médical algérien.
        </p>"""

        # Contact page content
        site_info.contact_intro_title = "Contactez l'Équipe"
        site_info.contact_intro_text = """<p>
            Vous recherchez un fournisseur d'équipements médicaux avec un personnel professionnel, 
            compétent et à l'écoute ? <strong>Fennec Med</strong> est là pour vous servir. Nous 
            comprenons que l'acquisition d'équipements médicaux est un investissement important, et 
            nous nous engageons à vous accompagner à chaque étape. Que vous souhaitiez obtenir un devis, 
            planifier une démonstration de produit, ou simplement poser des questions, notre équipe est 
            disponible pour vous aider.
        </p>"""
        site_info.contact_form_title = "Demande de Renseignements"
        site_info.contact_form_description = "Remplissez le formulaire ci-dessous et notre équipe vous contactera dans les plus brefs délais."

        site_info.map_embed_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d102893.08771533203!2d5.331841!3d36.19!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x128775c4d3e73515%3A0x8c4e5bb93c6cd3e4!2zU8OpdGlmLCBBbGfDqXJpZQ!5e0!3m2!1sfr!2sdz!4v1704067200000!5m2!1sfr!2sdz"

        site_info.save()
        self.stdout.write("Informations du site créées/mises à jour")

        # Create FAQs
        faqs_data = [
            {
                "category": "ordering",
                "question": "Comment passer une commande ?",
                "answer": "Vous pouvez passer commande directement sur notre site web après inscription. Pour les commandes importantes ou personnalisées, contactez notre équipe commerciale pour un devis adapté.",
                "order": 1,
            },
            {
                "category": "ordering",
                "question": "Quels sont les moyens de paiement acceptés ?",
                "answer": "Nous acceptons les paiements par virement bancaire, chèque certifié, et paiement à la livraison pour les clients réguliers. Le paiement en ligne sera disponible prochainement.",
                "order": 2,
            },
            {
                "category": "shipping",
                "question": "Quels sont vos délais de livraison ?",
                "answer": "Pour Sétif et environs : 24-48h. Pour les autres wilayas : 3-5 jours ouvrables. Livraison express disponible sur demande.",
                "order": 1,
            },
            {
                "category": "shipping",
                "question": "Livrez-vous dans toute l'Algérie ?",
                "answer": "Oui, nous livrons dans les 58 wilayas d'Algérie via notre réseau de partenaires logistiques fiables.",
                "order": 2,
            },
            {
                "category": "technical",
                "question": "Proposez-vous une formation sur les équipements ?",
                "answer": "Oui, nous offrons des formations gratuites sur l'utilisation et l'entretien des équipements pour tous les achats importants.",
                "order": 1,
            },
            {
                "category": "technical",
                "question": "Assurez-vous le service après-vente ?",
                "answer": "Absolument. Nous disposons d'une équipe technique qualifiée pour l'installation, la maintenance et les réparations de tous nos équipements.",
                "order": 2,
            },
            {
                "category": "warranty",
                "question": "Quelle est la durée de garantie ?",
                "answer": "Tous nos produits sont couverts par une garantie constructeur de 1 à 3 ans selon les équipements. Extensions de garantie disponibles.",
                "order": 1,
            },
            {
                "category": "warranty",
                "question": "Comment faire valoir la garantie ?",
                "answer": "Contactez notre service client avec votre facture et la description du problème. Nous interviendrons dans les 48h pour les équipements critiques.",
                "order": 2,
            },
            {
                "category": "returns",
                "question": "Puis-je retourner un produit ?",
                "answer": "Oui, retours acceptés sous 14 jours pour les produits non ouverts et en état neuf. Les équipements défectueux sont remplacés immédiatement.",
                "order": 1,
            },
            {
                "category": "returns",
                "question": "Quelles sont les conditions d'échange ?",
                "answer": "Les échanges sont possibles sous 30 jours avec présentation de la facture d'origine. Le produit doit être dans son emballage d'origine.",
                "order": 2,
            },
        ]

        for faq_data in faqs_data:
            FAQ.objects.get_or_create(question=faq_data["question"], defaults=faq_data)

        self.stdout.write(f"{len(faqs_data)} FAQ créées")

        # Create Testimonials
        testimonials_data = [
            {
                "name": "Dr Amina Benali",
                "position": "Médecin généraliste",
                "company": "Cabinet Médical El Amel",
                "content": "Excellents produits et service impeccable. L'équipe de Fennec Med m'a aidé à équiper mon cabinet avec du matériel de qualité à des prix compétitifs.",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Karim Messaoudi",
                "position": "Pharmacien",
                "company": "Pharmacie Centrale Sétif",
                "content": "Fournisseur sérieux et fiable. Livraison rapide et produits conformes aux normes. Je recommande vivement !",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Dr Rachid Boukhalfa",
                "position": "Chirurgien-dentiste",
                "company": "Cabinet Dentaire Sourire",
                "content": "Service après-vente exceptionnel. L'équipe technique est très compétente et toujours disponible. Très satisfait de mon équipement.",
                "rating": 5,
                "is_featured": True,
            },
            {
                "name": "Fatima Zerrouki",
                "position": "Directrice",
                "company": "Clinique des Hauts Plateaux",
                "content": "Partenaire de confiance pour notre clinique. Large choix d'équipements et conseils professionnels. Une vraie valeur ajoutée.",
                "rating": 5,
                "is_featured": False,
            },
            {
                "name": "Dr Mohamed Yahiaoui",
                "position": "Cardiologue",
                "company": "Hôpital Régional Sétif",
                "content": "Matériel de diagnostic de haute qualité. Les prix sont raisonnables et le service client est réactif. Excellent partenaire.",
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
                "name": "Dr Salim Boumediene",
                "email": "s.boumediene@clinique.dz",
                "phone": "+213 555 123 456",
                "inquiry_type": "general",
                "subject": "Demande de devis pour équipement radiologique",
                "message": "Bonjour, nous souhaitons équiper notre nouvelle clinique d'un appareil de radiologie numérique. Pourriez-vous nous envoyer un devis détaillé ?",
            },
            {
                "name": "Leila Cherif",
                "email": "l.cherif@pharmacie.dz",
                "phone": "+213 770 234 567",
                "inquiry_type": "technical",
                "subject": "Formation sur tensiomètre digital",
                "message": "J'ai acheté plusieurs tensiomètres digitaux. Proposez-vous une formation pour le personnel de ma pharmacie ?",
            },
            {
                "name": "Ahmed Tahar",
                "email": "a.tahar@labo.dz",
                "inquiry_type": "partnership",
                "subject": "Partenariat laboratoire d'analyses",
                "message": "Notre laboratoire cherche un fournisseur régulier pour nos consommables. Serait-il possible de discuter d'un partenariat à long terme ?",
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
