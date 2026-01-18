from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to="categories/", blank=True, verbose_name="Image")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    logo = models.ImageField(upload_to="brands/", blank=True, verbose_name="Logo")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"

    def __str__(self):
        return self.name


class BulkContainerType(models.Model):
    """Dynamic bulk container types (cartons, tanks, packages, etc.)"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    typical_capacity = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Capacité typique",
        help_text="Ex: 50 unités, 10L, etc.",
    )

    class Meta:
        verbose_name = "Type de conteneur en gros"
        verbose_name_plural = "Types de conteneurs en gros"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    SPECIALTIES = [
        ("dermatology", "Dermatologie"),
        ("ophthalmology", "Ophtalmologie"),
        ("nephrology", "Néphrologie"),
        ("cardiology", "Cardiologie"),
        ("orthopedics", "Orthopédie"),
        ("neurology", "Neurologie"),
        ("pediatrics", "Pédiatrie"),
        ("general", "Médecine Générale"),
    ]

    AVAILABILITY_STATUS = [
        ("in_stock", "En Stock"),
        ("out_of_stock", "Rupture de Stock"),
        ("pre_order", "Précommande"),
        ("discontinued", "Arrêté"),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom")
    slug = models.SlugField(unique=True, blank=True)
    categories = models.ManyToManyField(
        Category, related_name="products", blank=True, verbose_name="Catégories"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="products", verbose_name="Marque"
    )
    description = models.TextField(verbose_name="Description")
    short_description = models.CharField(
        max_length=500, verbose_name="Description courte"
    )
    # Price is now 0 by default - actual prices come from variants
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Prix"
    )
    # Legacy bulk fields - kept for backward compatibility but variants handle this now
    bulk_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Prix en gros (legacy)",
    )
    bulk_quantity = models.PositiveIntegerField(
        default=10, verbose_name="Quantité en gros (legacy)"
    )
    sku = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    stock_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Quantité en stock"
    )
    specialty = models.CharField(
        max_length=50, choices=SPECIALTIES, blank=True, verbose_name="Spécialité"
    )
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default="in_stock",
        verbose_name="Statut de disponibilité",
    )

    # Product specifications
    specifications = models.TextField(blank=True, verbose_name="Spécifications")
    compatibility = models.TextField(blank=True, verbose_name="Compatibilité")
    warranty = models.CharField(max_length=100, blank=True, verbose_name="Garantie")

    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Titre méta")
    meta_description = models.TextField(blank=True, verbose_name="Description méta")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    # Features
    featured = models.BooleanField(default=False, verbose_name="En vedette")
    trending = models.BooleanField(default=False, verbose_name="Tendance")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_review_count(self):
        return self.reviews.count()

    def get_price_range(self):
        """Get min and max prices from active variants"""
        variants = self.variants.filter(is_active=True)
        if not variants:
            return self.price, self.price

        prices = [v.get_total_price() for v in variants if v.get_total_price() > 0]
        if not prices:
            return self.price, self.price

        return min(prices), max(prices)


class ProductVariant(models.Model):
    PURCHASE_TYPE_CHOICES = [
        ("retail", "Détail"),
        ("bulk", "En Gros"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="Produit",
    )
    variant_title = models.CharField(
        max_length=100, verbose_name="Titre de la variante"
    )
    variant_value = models.CharField(
        max_length=100, verbose_name="Valeur de la variante"
    )

    # Purchase type selection
    purchase_type = models.CharField(
        max_length=10,
        choices=PURCHASE_TYPE_CHOICES,
        default="retail",
        verbose_name="Type d'achat",
    )

    # Retail fields
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Prix de détail",
    )

    # Bulk fields - dynamic container type
    bulk_container_type = models.ForeignKey(
        BulkContainerType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="variants",
        verbose_name="Type de conteneur",
    )
    units_per_container = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Unités par conteneur",
        help_text="Nombre d'unités de détail dans ce conteneur",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Prix unitaire",
        help_text="Prix d'une seule unité de détail",
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Prix de gros",
        help_text="Prix du conteneur complet",
    )

    stock_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Quantité en stock"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    display_order = models.PositiveIntegerField(
        default=0, verbose_name="Ordre d'affichage"
    )

    class Meta:
        ordering = ["display_order", "variant_title"]
        unique_together = ("product", "variant_title", "variant_value")
        verbose_name = "Variante de produit"
        verbose_name_plural = "Variantes de produit"

    def __str__(self):
        return f"{self.product.name} - {self.variant_title}: {self.variant_value} ({self.get_purchase_type_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.purchase_type == "bulk":
            if not all(
                [
                    self.bulk_container_type,
                    self.units_per_container,
                    self.unit_price,
                    self.wholesale_price,
                ]
            ):
                raise ValidationError(
                    "Pour l'achat en gros, veuillez remplir: type de conteneur, "
                    "unités par conteneur, prix unitaire et prix de gros."
                )
        elif self.purchase_type == "retail":
            if not self.retail_price:
                raise ValidationError(
                    "Pour l'achat au détail, veuillez spécifier le prix de détail."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_total_price(self):
        """Get the total price based on purchase type"""
        if self.purchase_type == "bulk" and self.wholesale_price:
            return self.wholesale_price
        elif self.purchase_type == "retail" and self.retail_price:
            return self.retail_price
        return 0

    def get_unit_price(self):
        """Get the per-unit price"""
        if self.purchase_type == "bulk" and self.unit_price:
            return self.unit_price
        elif self.purchase_type == "retail" and self.retail_price:
            return self.retail_price
        return 0

    def calculate_bulk_savings(self):
        """Calculate savings when buying in bulk vs retail"""
        if (
            self.purchase_type == "bulk"
            and self.unit_price
            and self.units_per_container
        ):
            retail_equivalent = self.unit_price * self.units_per_container
            if self.wholesale_price and retail_equivalent > self.wholesale_price:
                return retail_equivalent - self.wholesale_price
        return 0

    def get_savings_percentage(self):
        """Get savings percentage for bulk purchase"""
        savings = self.calculate_bulk_savings()
        if savings > 0 and self.unit_price and self.units_per_container:
            retail_equivalent = self.unit_price * self.units_per_container
            return (savings / retail_equivalent) * 100
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Produit"
    )
    image = models.ImageField(upload_to="products/", verbose_name="Image")
    alt_text = models.CharField(
        max_length=200, blank=True, verbose_name="Texte alternatif"
    )
    is_primary = models.BooleanField(default=False, verbose_name="Image principale")

    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produit"

    def __str__(self):
        return f"{self.product.name} - Image"


class ProductReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Produit",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name="Note")
    title = models.CharField(max_length=200, verbose_name="Titre")
    comment = models.TextField(verbose_name="Commentaire")
    verified_purchase = models.BooleanField(default=False, verbose_name="Achat vérifié")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]
        verbose_name = "Avis sur le produit"
        verbose_name_plural = "Avis sur les produits"

    def __str__(self):
        return f"{self.product.name} - {self.rating} étoiles"


class ProductQuestion(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Produit",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    question = models.TextField(verbose_name="Question")
    answer = models.TextField(blank=True, verbose_name="Réponse")
    answered_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answered_questions",
        blank=True,
        null=True,
        verbose_name="Répondu par",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    answered_at = models.DateTimeField(blank=True, null=True, verbose_name="Répondu le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Question sur le produit"
        verbose_name_plural = "Questions sur les produits"

    def __str__(self):
        return f"Question sur {self.product.name}"


class Wishlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="Utilisateur",
    )
    products = models.ManyToManyField(Product, blank=True, verbose_name="Produits")

    class Meta:
        verbose_name = "Liste de souhaits"
        verbose_name_plural = "Listes de souhaits"

    def __str__(self):
        return f"Liste de souhaits de {self.user.username}"
