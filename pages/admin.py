from django.contrib import admin
from .models import ContactMessage, FAQ, Testimonial, SiteInformation, TeamMember


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "inquiry_type",
        "subject",
        "created_at",
        "responded",
    ]
    list_filter = ["inquiry_type", "responded", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]
    list_editable = ["responded"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "category", "order", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["question", "answer"]
    list_editable = ["order", "is_active"]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "company",
        "position",
        "rating",
        "is_featured",
        "created_at",
    ]
    list_filter = ["rating", "is_featured", "created_at"]
    search_fields = ["name", "company", "content"]
    list_editable = ["is_featured"]


@admin.register(SiteInformation)
class SiteInformationAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Informations de base",
            {"fields": ("site_name", "tagline", "description", "logo", "tva_rate")},
        ),
        ("Coordonnées", {"fields": ("phone", "fax", "email", "address")}),
        (
            "Réseaux sociaux",
            {
                "fields": (
                    "facebook_url",
                    "instagram_url",
                    "whatsapp_url",
                    "youtube_url",
                    "linkedin_url",
                )
            },
        ),
        (
            "Contenu de la page À propos",
            {
                "fields": (
                    "about_hero_title",
                    "about_hero_description",
                    "about_story_title",
                    "about_story_content",
                    "about_image_1",
                    "about_image_2",
                )
            },
        ),
        ("Carte", {"fields": ("map_embed_url",)}),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        if SiteInformation.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton
        return False


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "position",
        "role",
        "order",
        "is_active",
        "show_on_about_page",
    ]
    list_filter = ["role", "is_active", "show_on_about_page"]
    search_fields = ["name", "position", "bio"]
    list_editable = ["order", "is_active", "show_on_about_page"]

    fieldsets = (
        (
            "Informations de base",
            {"fields": ("name", "position", "role", "bio", "image")},
        ),
        (
            "Coordonnées",
            {"fields": ("email", "phone", "linkedin_url"), "classes": ("collapse",)},
        ),
        (
            "Options d'affichage",
            {"fields": ("order", "is_active", "show_on_about_page")},
        ),
    )
