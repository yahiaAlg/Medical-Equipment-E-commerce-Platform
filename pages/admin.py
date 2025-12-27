from django.contrib import admin
from .models import ContactMessage, FAQ, Testimonial


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "inquiry_type",
        "subject",
        "created_at",
        "responded",
    )
    list_filter = ("inquiry_type", "responded", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    list_editable = ("responded",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("Contact Information", {"fields": ("name", "email", "phone")}),
        ("Inquiry Details", {"fields": ("inquiry_type", "subject", "message")}),
        ("Status", {"fields": ("responded", "created_at")}),
    )

    actions = ["mark_as_responded", "mark_as_not_responded"]

    def mark_as_responded(self, request, queryset):
        updated = queryset.update(responded=True)
        self.message_user(request, f"{updated} message(s) marked as responded.")

    mark_as_responded.short_description = "Mark selected messages as responded"

    def mark_as_not_responded(self, request, queryset):
        updated = queryset.update(responded=False)
        self.message_user(request, f"{updated} message(s) marked as not responded.")

    mark_as_not_responded.short_description = "Mark selected messages as not responded"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "order", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("question", "answer")
    list_editable = ("order", "is_active")

    fieldsets = (
        ("FAQ Content", {"fields": ("category", "question", "answer")}),
        ("Display Settings", {"fields": ("order", "is_active")}),
    )

    actions = ["activate_faqs", "deactivate_faqs"]

    def activate_faqs(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} FAQ(s) activated.")

    activate_faqs.short_description = "Activate selected FAQs"

    def deactivate_faqs(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} FAQ(s) deactivated.")

    deactivate_faqs.short_description = "Deactivate selected FAQs"


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "position",
        "rating",
        "is_featured",
        "created_at",
    )
    list_filter = ("rating", "is_featured", "created_at")
    search_fields = ("name", "company", "position", "content")
    readonly_fields = ("created_at",)
    list_editable = ("is_featured",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("Person Information", {"fields": ("name", "position", "company", "image")}),
        ("Testimonial Content", {"fields": ("content", "rating")}),
        ("Display Settings", {"fields": ("is_featured", "created_at")}),
    )

    actions = ["feature_testimonials", "unfeature_testimonials"]

    def feature_testimonials(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} testimonial(s) featured.")

    feature_testimonials.short_description = "Feature selected testimonials"

    def unfeature_testimonials(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} testimonial(s) unfeatured.")

    unfeature_testimonials.short_description = "Unfeature selected testimonials"
