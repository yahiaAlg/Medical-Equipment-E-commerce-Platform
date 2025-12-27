from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("added_at", "get_total_price")
    fields = ("product", "quantity", "added_at", "get_total_price")

    def get_total_price(self, obj):
        if obj.pk:
            return f"${obj.get_total_price():.2f}"
        return "-"

    get_total_price.short_description = "Total Price"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_total_items",
        "get_total_price",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "get_total_items", "get_total_price")
    inlines = [CartItemInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("items__product")
        )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "get_total_price", "added_at")
    list_filter = ("added_at",)
    search_fields = ("cart__user__username", "product__name")
    readonly_fields = ("added_at", "get_total_price")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("cart__user", "product")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("get_total_price",)
    fields = ("product", "quantity", "price", "get_total_price")

    def get_total_price(self, obj):
        if obj.pk:
            return f"${obj.get_total_price():.2f}"
        return "-"

    get_total_price.short_description = "Total Price"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "status",
        "payment_method",
        "total_amount",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_method",
        "created_at",
        "shipped_at",
        "delivered_at",
    )
    search_fields = (
        "order_id",
        "user__username",
        "user__email",
        "tracking_number",
        "payment_reference",
    )
    readonly_fields = ("order_id", "created_at", "updated_at")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]

    fieldsets = (
        (
            "Order Information",
            {"fields": ("order_id", "user", "status", "tracking_number")},
        ),
        (
            "Shipping Address",
            {
                "fields": (
                    "shipping_address",
                    "shipping_city",
                    "shipping_state",
                    "shipping_zip",
                    "shipping_country",
                )
            },
        ),
        (
            "Billing Address",
            {
                "fields": (
                    "billing_address",
                    "billing_city",
                    "billing_state",
                    "billing_zip",
                    "billing_country",
                )
            },
        ),
        ("Payment", {"fields": ("payment_method", "payment_reference")}),
        (
            "Pricing",
            {"fields": ("subtotal", "tax_amount", "shipping_cost", "total_amount")},
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "shipped_at", "delivered_at"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "mark_as_confirmed",
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
    ]

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status="confirmed")
        self.message_user(request, f"{updated} order(s) marked as confirmed.")

    mark_as_confirmed.short_description = "Mark as Confirmed"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status="processing")
        self.message_user(request, f"{updated} order(s) marked as processing.")

    mark_as_processing.short_description = "Mark as Processing"

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="shipped", shipped_at=timezone.now())
        self.message_user(request, f"{updated} order(s) marked as shipped.")

    mark_as_shipped.short_description = "Mark as Shipped"

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="delivered", delivered_at=timezone.now())
        self.message_user(request, f"{updated} order(s) marked as delivered.")

    mark_as_delivered.short_description = "Mark as Delivered"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("items__product")
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "get_total_price")
    search_fields = ("order__order_id", "product__name")
    readonly_fields = ("get_total_price",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order", "product")
