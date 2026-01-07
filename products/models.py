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
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    bulk_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Prix en gros",
    )
    bulk_quantity = models.PositiveIntegerField(
        default=10, verbose_name="Quantité en gros"
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


class ProductVariant(models.Model):
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
    additional_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Coût additionnel"
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
        return f"{self.product.name} - {self.variant_title}: {self.variant_value}"

    def get_total_price(self):
        return self.product.price + self.additional_cost


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
