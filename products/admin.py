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
        ("Category Information", {"fields": ("name", "slug", "description", "image")}),
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")

    fieldsets = (("Brand Information", {"fields": ("name", "logo", "description")}),)


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
        "get_categories",  # Updated
        "brand",
        "price",
        "bulk_price",
        "stock_quantity",
        "availability_status",
        "featured",
        "trending",
    )
    list_filter = (
        "categories",  # Updated
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
    filter_horizontal = ("categories",)  # Added

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "slug", "categories", "brand", "sku")},
        ),  # Updated
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
            "Pricing & Inventory",
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
        ("Features & Status", {"fields": ("featured", "trending")}),
        (
            "Reviews",
            {
                "fields": ("get_average_rating", "get_review_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
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
        self.message_user(request, f"{updated} product(s) marked as featured.")

    mark_as_featured.short_description = "Mark as Featured"

    def mark_as_trending(self, request, queryset):
        updated = queryset.update(trending=True)
        self.message_user(request, f"{updated} product(s) marked as trending.")

    mark_as_trending.short_description = "Mark as Trending"

    def mark_in_stock(self, request, queryset):
        updated = queryset.update(availability_status="in_stock")
        self.message_user(request, f"{updated} product(s) marked as in stock.")

    mark_in_stock.short_description = "Mark as In Stock"

    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(availability_status="out_of_stock")
        self.message_user(request, f"{updated} product(s) marked as out of stock.")

    mark_out_of_stock.short_description = "Mark as Out of Stock"

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    get_categories.short_description = "Categories"

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
    list_filter = ("is_active", "variant_title", "product__categories")  # Changed here
    search_fields = ("product__name", "variant_title", "variant_value")
    list_editable = ("is_active", "display_order", "stock_quantity")
    ordering = ("product", "display_order", "variant_title")

    fieldsets = (
        (
            "Variant Information",
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
            "Inventory & Display",
            {"fields": ("stock_quantity", "is_active", "display_order")},
        ),
    )

    actions = ["activate_variants", "deactivate_variants"]

    def activate_variants(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} variant(s) activated.")

    activate_variants.short_description = "Activate selected variants"

    def deactivate_variants(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} variant(s) deactivated.")

    deactivate_variants.short_description = "Deactivate selected variants"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("product", "product__brand")
            .prefetch_related("product__categories")  # Changed here too
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
            "Review Information",
            {"fields": ("product", "user", "rating", "verified_purchase")},
        ),
        ("Review Content", {"fields": ("title", "comment")}),
        ("Timestamp", {"fields": ("created_at",)}),
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
        ("Answer", {"fields": ("answer", "answered_by", "answered_at")}),
    )

    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question

    question_preview.short_description = "Question"

    def answer_preview(self, obj):
        if obj.answer:
            return obj.answer[:50] + "..." if len(obj.answer) > 50 else obj.answer
        return "-"

    answer_preview.short_description = "Answer"

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

    product_count.short_description = "Number of Products"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("products")
        )
