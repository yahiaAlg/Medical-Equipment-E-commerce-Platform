from django.contrib import admin
from .models import (
    Cart,
    CartItem,
    ShippingType,
    Order,
    OrderItem,
    OrderNote,
    OrderNoteAttachment,
    Invoice,
    PaymentProof,
    PaymentReceipt,
    Complaint,
    ComplaintReason,
    ComplaintAttachment,
    Refund,
    RefundProof,
    RefundReceipt,
    Notification,
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("added_at", "get_total_price")
    fields = ("product", "variant", "quantity", "added_at", "get_total_price")
    verbose_name = "Article"
    verbose_name_plural = "Articles"

    def get_total_price(self, obj):
        if obj.pk:
            return f"{obj.get_total_price()} DZD"
        return "-"

    get_total_price.short_description = "Prix total"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_total_items",
        "display_total_price",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "user__email")
    readonly_fields = (
        "created_at",
        "updated_at",
        "get_total_items",
        "display_total_price",
    )
    inlines = [CartItemInline]

    def display_total_price(self, obj):
        return f"{obj.get_total_price()} DZD"

    display_total_price.short_description = "Prix total"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("items__product")
        )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "variant",
        "quantity",
        "display_total_price",
        "added_at",
    )
    list_filter = ("added_at",)
    search_fields = ("cart__user__username", "product__name")
    readonly_fields = ("added_at", "display_total_price")

    def display_total_price(self, obj):
        return f"{obj.get_total_price()} DZD"

    display_total_price.short_description = "Prix total"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("cart__user", "product", "variant")
        )


@admin.register(ShippingType)
class ShippingTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "cost", "estimated_days", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("get_total_price",)
    fields = ("product", "quantity", "price", "get_total_price")
    verbose_name = "Article"
    verbose_name_plural = "Articles"

    def get_total_price(self, obj):
        if obj.pk:
            return f"{obj.get_total_price()} DZD"
        return "-"

    get_total_price.short_description = "Prix total"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "status",
        "shipping_type",
        "display_total_amount",
        "created_at",
        "paid_at",
    )
    list_filter = (
        "status",
        "shipping_type",
        "created_at",
        "confirmed_at",
        "paid_at",
        "shipped_at",
        "delivered_at",
    )
    search_fields = (
        "order_id",
        "user__username",
        "user__email",
        "tracking_number",
    )
    readonly_fields = ("order_id", "created_at", "updated_at")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]

    fieldsets = (
        (
            "Informations de commande",
            {"fields": ("order_id", "user", "status", "tracking_number")},
        ),
        (
            "Livraison",
            {
                "fields": (
                    "shipping_type",
                    "shipping_address",
                    "shipping_city",
                    "shipping_state",
                    "shipping_zip",
                    "shipping_country",
                )
            },
        ),
        (
            "Tarification",
            {"fields": ("subtotal", "tax_amount", "shipping_cost", "total_amount")},
        ),
        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "confirmed_at",
                    "rejected_at",
                    "paid_at",
                    "shipped_at",
                    "delivered_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "mark_as_confirmed",
        "mark_as_paid",
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
    ]

    def display_total_amount(self, obj):
        return f"{obj.total_amount} DZD"

    display_total_amount.short_description = "Montant total"

    def mark_as_confirmed(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(status="pending_confirmation").update(
            status="confirmed", confirmed_at=timezone.now()
        )
        self.message_user(request, f"{updated} commande(s) confirmée(s).")

    mark_as_confirmed.short_description = "Confirmer les commandes"

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="paid", paid_at=timezone.now())
        self.message_user(request, f"{updated} commande(s) marquée(s) comme payée(s).")

    mark_as_paid.short_description = "Marquer comme payée"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status="processing")
        self.message_user(request, f"{updated} commande(s) marquée(s) en traitement.")

    mark_as_processing.short_description = "Marquer en traitement"

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="shipped", shipped_at=timezone.now())
        self.message_user(
            request, f"{updated} commande(s) marquée(s) comme expédiée(s)."
        )

    mark_as_shipped.short_description = "Marquer comme expédiée"

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="delivered", delivered_at=timezone.now())
        self.message_user(request, f"{updated} commande(s) marquée(s) comme livrée(s).")

    mark_as_delivered.short_description = "Marquer comme livrée"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "shipping_type")
            .prefetch_related("items__product")
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "display_total_price")
    search_fields = ("order__order_id", "product__name")
    readonly_fields = ("display_total_price",)

    def display_total_price(self, obj):
        return f"{obj.get_total_price()} DZD"

    display_total_price.short_description = "Prix total"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order", "product")


class OrderNoteAttachmentInline(admin.TabularInline):
    model = OrderNoteAttachment
    extra = 0
    readonly_fields = ("uploaded_at",)
    verbose_name = "Pièce jointe"
    verbose_name_plural = "Pièces jointes"


@admin.register(OrderNote)
class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ("order", "created_by", "created_at", "updated_at")
    search_fields = ("order__order_id", "content")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("created_at",)
    inlines = [OrderNoteAttachmentInline]


@admin.register(OrderNoteAttachment)
class OrderNoteAttachmentAdmin(admin.ModelAdmin):
    list_display = ("order_note", "file_name", "file_type", "uploaded_at")
    search_fields = ("order_note__order__order_id", "file_name")
    readonly_fields = ("uploaded_at",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "order",
        "status",
        "total_amount",
        "created_at",
        "paid_at",
    )
    list_filter = ("status", "created_at", "paid_at")
    search_fields = ("invoice_number", "order__order_id", "order__user__username")
    readonly_fields = ("invoice_number", "created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "payment_method",
        "verified",
        "uploaded_at",
        "verified_by",
    )
    list_filter = ("verified", "payment_method", "uploaded_at")
    search_fields = ("invoice__invoice_number", "transaction_reference")
    readonly_fields = ("uploaded_at", "updated_at")

    actions = ["approve_payments", "reject_payments"]

    def approve_payments(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(
            verified=True, verified_by=request.user, verified_at=timezone.now()
        )
        self.message_user(request, f"{updated} paiement(s) approuvé(s).")

    approve_payments.short_description = "Approuver les paiements sélectionnés"

    def reject_payments(self, request, queryset):
        self.message_user(
            request,
            "Veuillez rejeter les paiements individuellement avec un motif.",
            level="warning",
        )

    reject_payments.short_description = "Rejeter les paiements sélectionnés"


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "invoice", "amount_paid", "payment_date")
    search_fields = ("receipt_number", "invoice__invoice_number")
    readonly_fields = ("receipt_number", "generated_at")


@admin.register(ComplaintReason)
class ComplaintReasonAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "display_order")
    list_editable = ("is_active", "display_order")
    list_filter = ("is_active",)


class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0
    readonly_fields = ("uploaded_at",)
    verbose_name = "Pièce jointe"
    verbose_name_plural = "Pièces jointes"


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "complaint_number",
        "user",
        "order",
        "status",
        "reason",
        "created_at",
    )
    list_filter = ("status", "created_at", "reason")
    search_fields = ("complaint_number", "user__username", "order__order_id")
    readonly_fields = ("complaint_number", "created_at", "updated_at")
    inlines = [ComplaintAttachmentInline]

    fieldsets = (
        (
            "Informations de réclamation",
            {"fields": ("complaint_number", "user", "order", "invoice", "status")},
        ),
        ("Détails", {"fields": ("reason", "custom_reason", "description")}),
        (
            "Réponse administrateur",
            {
                "fields": (
                    "admin_notes",
                    "resolution_notes",
                    "handled_by",
                    "resolved_at",
                )
            },
        ),
        (
            "Dates",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("refund_number", "order", "amount", "status", "created_at")
    list_filter = ("status", "refund_method", "created_at")
    search_fields = ("refund_number", "order__order_id")
    readonly_fields = ("refund_number", "created_at")


@admin.register(RefundProof)
class RefundProofAdmin(admin.ModelAdmin):
    list_display = ("refund", "uploaded_by", "uploaded_at")
    search_fields = ("refund__refund_number", "transaction_reference")
    readonly_fields = ("uploaded_at",)


@admin.register(RefundReceipt)
class RefundReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "refund", "amount_refunded", "refund_date")
    search_fields = ("receipt_number", "refund__refund_number")
    readonly_fields = ("receipt_number", "generated_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
