from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="brands/", blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    SPECIALTIES = [
        ("dermatology", "Dermatology"),
        ("ophthalmology", "Ophthalmology"),
        ("nephrology", "Nephrology"),
        ("cardiology", "Cardiology"),
        ("orthopedics", "Orthopedics"),
        ("neurology", "Neurology"),
        ("pediatrics", "Pediatrics"),
        ("general", "General Medicine"),
    ]

    AVAILABILITY_STATUS = [
        ("in_stock", "In Stock"),
        ("out_of_stock", "Out of Stock"),
        ("pre_order", "Pre-Order"),
        ("discontinued", "Discontinued"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bulk_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    bulk_quantity = models.PositiveIntegerField(default=10)
    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    specialty = models.CharField(max_length=50, choices=SPECIALTIES, blank=True)
    availability_status = models.CharField(
        max_length=20, choices=AVAILABILITY_STATUS, default="in_stock"
    )

    # Product specifications
    specifications = models.TextField(blank=True)
    compatibility = models.TextField(blank=True)
    warranty = models.CharField(max_length=100, blank=True)

    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Features
    featured = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

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
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    variant_title = models.CharField(max_length=100)  # e.g., "Size", "Color", "Volume"
    variant_value = models.CharField(max_length=100)  # e.g., "5 lbs", "Red", "500ml"
    additional_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "variant_title"]
        unique_together = ("product", "variant_title", "variant_value")

    def __str__(self):
        return f"{self.product.name} - {self.variant_title}: {self.variant_value}"

    def get_total_price(self):
        return self.product.price + self.additional_cost


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - Image"


class ProductReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"


class ProductQuestion(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="questions"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)
    answered_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answered_questions",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Question about {self.product.name}"


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"
