from django.contrib import admin
from .models import (
    Category,
    Brand,
    Product,
    ProductVariant,
    ProductImage,
    ProductReview,
    ProductQuestion,
    Wishlist,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (
            "Informations sur la catégorie",
            {"fields": ("name", "slug", "description", "image")},
        ),
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")

    fieldsets = (
        ("Informations sur la marque", {"fields": ("name", "logo", "description")}),
    )


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "variant_title",
        "variant_value",
        "additional_cost",
        "stock_quantity",
        "is_active",
        "display_order",
    )
    ordering = ("display_order", "variant_title")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary")


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ("user", "rating", "created_at")
    fields = ("user", "rating", "title", "verified_purchase", "created_at")
    can_delete = True


class ProductQuestionInline(admin.TabularInline):
    model = ProductQuestion
    extra = 0
    readonly_fields = ("user", "question", "created_at")
    fields = ("user", "question", "answer", "answered_by", "answered_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_categories",
        "brand",
        "price",
        "bulk_price",
        "stock_quantity",
        "availability_status",
        "featured",
        "trending",
    )
    list_filter = (
        "categories",
        "brand",
        "specialty",
        "availability_status",
        "featured",
        "trending",
        "created_at",
    )
    search_fields = ("name", "sku", "description", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = (
        "created_at",
        "updated_at",
        "get_average_rating",
        "get_review_count",
    )
    list_editable = ("featured", "trending", "availability_status")
    date_hierarchy = "created_at"
    inlines = [
        ProductVariantInline,
        ProductImageInline,
        ProductReviewInline,
        ProductQuestionInline,
    ]
    filter_horizontal = ("categories",)

    fieldsets = (
        (
            "Informations de base",
            {"fields": ("name", "slug", "categories", "brand", "sku")},
        ),
        (
            "Description",
            {
                "fields": (
                    "short_description",
                    "description",
                    "specifications",
                    "compatibility",
                )
            },
        ),
        (
            "Prix et inventaire",
            {
                "fields": (
                    "price",
                    "bulk_price",
                    "bulk_quantity",
                    "stock_quantity",
                    "availability_status",
                )
            },
        ),
        ("Classification", {"fields": ("specialty", "warranty")}),
        (
            "SEO",
            {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)},
        ),
        ("Caractéristiques et statut", {"fields": ("featured", "trending")}),
        (
            "Avis",
            {
                "fields": ("get_average_rating", "get_review_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Horodatage",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = [
        "mark_as_featured",
        "mark_as_trending",
        "mark_in_stock",
        "mark_out_of_stock",
    ]

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f"{updated} produit(s) marqué(s) en vedette.")

    mark_as_featured.short_description = "Marquer en vedette"

    def mark_as_trending(self, request, queryset):
        updated = queryset.update(trending=True)
        self.message_user(request, f"{updated} produit(s) marqué(s) en tendance.")

    mark_as_trending.short_description = "Marquer en tendance"

    def mark_in_stock(self, request, queryset):
        updated = queryset.update(availability_status="in_stock")
        self.message_user(request, f"{updated} produit(s) marqué(s) en stock.")

    mark_in_stock.short_description = "Marquer en stock"

    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(availability_status="out_of_stock")
        self.message_user(
            request, f"{updated} produit(s) marqué(s) en rupture de stock."
        )

    mark_out_of_stock.short_description = "Marquer en rupture de stock"

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    get_categories.short_description = "Catégories"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("categories", "images", "reviews", "variants")
            .select_related("brand")
        )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "variant_title",
        "variant_value",
        "additional_cost",
        "stock_quantity",
        "is_active",
        "display_order",
    )
    list_filter = ("is_active", "variant_title", "product__categories")
    search_fields = ("product__name", "variant_title", "variant_value")
    list_editable = ("is_active", "display_order", "stock_quantity")
    ordering = ("product", "display_order", "variant_title")

    fieldsets = (
        (
            "Informations sur la variante",
            {
                "fields": (
                    "product",
                    "variant_title",
                    "variant_value",
                    "additional_cost",
                )
            },
        ),
        (
            "Inventaire et affichage",
            {"fields": ("stock_quantity", "is_active", "display_order")},
        ),
    )

    actions = ["activate_variants", "deactivate_variants"]

    def activate_variants(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} variante(s) activée(s).")

    activate_variants.short_description = "Activer les variantes sélectionnées"

    def deactivate_variants(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} variante(s) désactivée(s).")

    deactivate_variants.short_description = "Désactiver les variantes sélectionnées"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("product", "product__brand")
            .prefetch_related("product__categories")
        )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt_text", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("product__name", "alt_text")
    list_editable = ("is_primary",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "title",
        "verified_purchase",
        "created_at",
    )
    list_filter = ("rating", "verified_purchase", "created_at")
    search_fields = ("product__name", "user__username", "title", "comment")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Informations sur l'avis",
            {"fields": ("product", "user", "rating", "verified_purchase")},
        ),
        ("Contenu de l'avis", {"fields": ("title", "comment")}),
        ("Horodatage", {"fields": ("created_at",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("product", "user")


@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "question_preview",
        "answer_preview",
        "answered_by",
        "created_at",
        "answered_at",
    )
    list_filter = ("created_at", "answered_at")
    search_fields = ("product__name", "user__username", "question", "answer")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("Question", {"fields": ("product", "user", "question", "created_at")}),
        ("Réponse", {"fields": ("answer", "answered_by", "answered_at")}),
    )

    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question

    question_preview.short_description = "Question"

    def answer_preview(self, obj):
        if obj.answer:
            return obj.answer[:50] + "..." if len(obj.answer) > 50 else obj.answer
        return "-"

    answer_preview.short_description = "Réponse"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("product", "user", "answered_by")
        )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product_count")
    search_fields = ("user__username", "user__email")
    filter_horizontal = ("products",)

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Nombre de produits"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("products")
        )
