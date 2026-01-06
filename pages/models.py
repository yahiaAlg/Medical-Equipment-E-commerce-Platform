from django.db import models


class ContactMessage(models.Model):
    INQUIRY_TYPES = [
        ("general", "General Inquiry"),
        ("technical", "Technical Support"),
        ("partnership", "Partnership"),
        ("complaint", "Complaint"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class FAQ(models.Model):
    CATEGORIES = [
        ("ordering", "Ordering"),
        ("shipping", "Shipping"),
        ("technical", "Technical Support"),
        ("warranty", "Warranties"),
        ("returns", "Returns & Exchanges"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORIES)
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "order"]

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to="testimonials/", blank=True)
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], default=5
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.company}"


class SiteInformation(models.Model):
    """Singleton model for site-wide information"""

    site_name = models.CharField(max_length=100, default="Fennec Med")
    tagline = models.CharField(max_length=200, default="Quality Medical Supplies")
    description = models.TextField(blank=True)

    # Contact Information
    phone = models.CharField(max_length=20, default="(123) 456-7890")
    fax = models.CharField(max_length=20, blank=True)
    email = models.EmailField(default="info@fennecmed.com")
    address = models.TextField(default="123 Medical St, Brighton, VIC 3186")

    # Social Media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    whatsapp_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    # About Page Content
    about_hero_title = models.CharField(
        max_length=200, default="Quality Medical Supplies You Can Trust"
    )
    about_hero_description = models.TextField(blank=True)
    about_story_title = models.CharField(max_length=200, default="Our Story")
    about_story_content = models.TextField(blank=True)

    # Tax Configuration
    tva_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0.05,
        help_text="TVA/Tax rate as decimal (e.g., 0.19 for 19%)",
    )

    # Map
    map_embed_url = models.URLField(blank=True, help_text="Google Maps embed URL")

    # Images
    logo = models.ImageField(upload_to="site/", blank=True)
    about_image_1 = models.ImageField(upload_to="site/about/", blank=True)
    about_image_2 = models.ImageField(upload_to="site/about/", blank=True)

    # Meta
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Information"
        verbose_name_plural = "Site Information"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteInformation.objects.exists():
            raise ValueError("Only one SiteInformation instance allowed")
        return super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class TeamMember(models.Model):
    POSITION_CHOICES = [
        ("founder", "Founder"),
        ("ceo", "CEO"),
        ("manager", "Manager"),
        ("specialist", "Medical Specialist"),
        ("technician", "Technician"),
        ("sales", "Sales Representative"),
        ("support", "Customer Support"),
    ]

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=POSITION_CHOICES, default="support")
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="team/", blank=True)

    # Contact (optional)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Social Media (optional)
    linkedin_url = models.URLField(blank=True)

    # Display Options
    order = models.PositiveIntegerField(
        default=0, help_text="Display order (lower numbers first)"
    )
    is_active = models.BooleanField(default=True)
    show_on_about_page = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} - {self.position}"
