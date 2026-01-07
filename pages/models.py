from django.db import models


class ContactMessage(models.Model):
    INQUIRY_TYPES = [
        ("general", "Demande générale"),
        ("technical", "Support technique"),
        ("partnership", "Partenariat"),
        ("complaint", "Réclamation"),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Adresse e-mail")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    inquiry_type = models.CharField(
        max_length=20, choices=INQUIRY_TYPES, verbose_name="Type de demande"
    )
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    responded = models.BooleanField(default=False, verbose_name="Répondu")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.name} - {self.subject}"


class FAQ(models.Model):
    CATEGORIES = [
        ("ordering", "Commandes"),
        ("shipping", "Livraison"),
        ("technical", "Support technique"),
        ("warranty", "Garanties"),
        ("returns", "Retours et échanges"),
    ]

    category = models.CharField(
        max_length=20, choices=CATEGORIES, verbose_name="Catégorie"
    )
    question = models.CharField(max_length=300, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        ordering = ["category", "order"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    position = models.CharField(max_length=100, verbose_name="Poste")
    company = models.CharField(max_length=100, verbose_name="Entreprise")
    content = models.TextField(verbose_name="Contenu")
    image = models.ImageField(
        upload_to="testimonials/", blank=True, verbose_name="Image"
    )
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], default=5, verbose_name="Note"
    )
    is_featured = models.BooleanField(default=False, verbose_name="En vedette")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"

    def __str__(self):
        return f"{self.name} - {self.company}"


class SiteInformation(models.Model):
    """Modèle singleton pour les informations globales du site"""

    site_name = models.CharField(
        max_length=100, default="Fennec Med", verbose_name="Nom du site"
    )
    tagline = models.CharField(
        max_length=200,
        default="Fournitures médicales de qualité",
        verbose_name="Slogan",
    )
    description = models.TextField(blank=True, verbose_name="Description")

    # Contact Information
    phone = models.CharField(
        max_length=20, default="(123) 456-7890", verbose_name="Téléphone"
    )
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    email = models.EmailField(
        default="info@fennecmed.com", verbose_name="Adresse e-mail"
    )
    address = models.TextField(
        default="123 Medical St, Brighton, VIC 3186", verbose_name="Adresse"
    )

    # Social Media
    facebook_url = models.URLField(blank=True, verbose_name="URL Facebook")
    instagram_url = models.URLField(blank=True, verbose_name="URL Instagram")
    whatsapp_url = models.URLField(blank=True, verbose_name="URL WhatsApp")
    youtube_url = models.URLField(blank=True, verbose_name="URL YouTube")
    linkedin_url = models.URLField(blank=True, verbose_name="URL LinkedIn")

    # Home Page Content
    hero_title = models.CharField(
        max_length=200,
        default="Bienvenue chez Fennec Med",
        verbose_name="Titre Hero (Page d'accueil)",
    )
    hero_subtitle = models.TextField(
        default="Fournisseur de matériaux médicaux de qualité aux familles de la région depuis 2022.",
        verbose_name="Sous-titre Hero (Page d'accueil)",
    )
    about_section_title = models.CharField(
        max_length=200,
        default="À Propos de Notre Cabinet Basé à Brighton",
        verbose_name="Titre section À propos (Page d'accueil)",
    )
    find_us_content = models.TextField(
        blank=True,
        verbose_name="Contenu 'Où Nous Trouver' (Page d'accueil)",
        help_text="Texte pour la section 'Où Nous Trouver' sur la page d'accueil",
    )
    cta_title = models.CharField(
        max_length=200,
        default="Prêt à Franchir la Prochaine Étape ?",
        verbose_name="Titre CTA (Page d'accueil)",
    )
    cta_description = models.TextField(
        default="Contactez-nous aujourd'hui pour en savoir plus sur nos matériaux médicaux et services.",
        verbose_name="Description CTA (Page d'accueil)",
    )

    # About Page Content
    about_hero_title = models.CharField(
        max_length=200,
        default="Fournitures médicales de qualité en qui vous pouvez avoir confiance",
        verbose_name="Titre principal de la page À propos",
    )
    about_hero_description = models.TextField(
        blank=True, verbose_name="Description principale de la page À propos"
    )
    about_story_title = models.CharField(
        max_length=200, default="Notre histoire", verbose_name="Titre de l'histoire"
    )
    about_story_content = models.TextField(
        blank=True, verbose_name="Contenu de l'histoire"
    )

    # Contact Page Content
    contact_intro_title = models.CharField(
        max_length=200,
        default="Contactez l'Équipe",
        verbose_name="Titre intro (Page contact)",
    )
    contact_intro_text = models.TextField(
        blank=True,
        verbose_name="Texte intro (Page contact)",
        help_text="Texte d'introduction sur la page de contact",
    )
    contact_form_title = models.CharField(
        max_length=200,
        default="Demande de Renseignements",
        verbose_name="Titre formulaire (Page contact)",
    )
    contact_form_description = models.TextField(
        default="Si vous préférez nous contacter par email, veuillez remplir vos coordonnées et nous vous répondrons bientôt.",
        verbose_name="Description formulaire (Page contact)",
    )

    # Tax Configuration
    tva_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0.05,
        help_text="Taux de TVA en décimal (ex. : 0,19 pour 19%)",
        verbose_name="Taux de TVA",
    )

    # Map
    map_embed_url = models.URLField(
        blank=True,
        help_text="URL d'intégration Google Maps",
        verbose_name="URL de la carte",
    )

    # Images
    logo = models.ImageField(upload_to="site/", blank=True, verbose_name="Logo")
    about_image_1 = models.ImageField(
        upload_to="site/about/", blank=True, verbose_name="Image À propos 1"
    )
    about_image_2 = models.ImageField(
        upload_to="site/about/", blank=True, verbose_name="Image À propos 2"
    )

    # Meta
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Informations du site"
        verbose_name_plural = "Informations du site"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteInformation.objects.exists():
            raise ValueError("Une seule instance de SiteInformation est autorisée")
        return super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Obtenir ou créer l'instance singleton"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class TeamMember(models.Model):
    POSITION_CHOICES = [
        ("founder", "Fondateur"),
        ("ceo", "Directeur général"),
        ("manager", "Responsable"),
        ("specialist", "Spécialiste médical"),
        ("technician", "Technicien"),
        ("sales", "Représentant commercial"),
        ("support", "Support client"),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom")
    position = models.CharField(max_length=100, verbose_name="Poste")
    role = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="support",
        verbose_name="Rôle",
    )
    bio = models.TextField(blank=True, verbose_name="Biographie")
    image = models.ImageField(upload_to="team/", blank=True, verbose_name="Image")

    # Contact (optional)
    email = models.EmailField(blank=True, verbose_name="Adresse e-mail")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")

    # Social Media (optional)
    linkedin_url = models.URLField(blank=True, verbose_name="URL LinkedIn")

    # Display Options
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordre d'affichage (les nombres inférieurs en premier)",
        verbose_name="Ordre",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    show_on_about_page = models.BooleanField(
        default=True, verbose_name="Afficher sur la page À propos"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"

    def __str__(self):
        return f"{self.name} - {self.position}"
