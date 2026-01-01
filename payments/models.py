from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import uuid


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        if self.quantity >= self.product.bulk_quantity and self.product.bulk_price:
            return self.quantity * self.product.bulk_price
        return self.quantity * self.product.price


class Order(models.Model):
    STATUS_CHOICES = [
        ("awaiting_payment", "Awaiting Payment"),
        ("payment_under_review", "Payment Under Review"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refund_pending", "Refund Pending"),
        ("refunded", "Refunded"),
    ]

    order_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="awaiting_payment"
    )

    # Shipping information
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=10)
    shipping_country = models.CharField(max_length=100, default="Algeria")

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_id}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("payment_submitted", "Payment Submitted"),
        ("payment_rejected", "Payment Rejected"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="invoice"
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="unpaid")

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment instructions
    payment_instructions = models.TextField(
        default=(
            "Please make payment via one of the following methods:\n"
            "1. BaridiMob: +213 XXX XXX XXX\n"
            "2. CCP: XXXXXX Clé XX\n"
            "3. Bank Transfer: IBAN DZXX XXXX XXXX XXXX XXXX\n"
            "After payment, upload your proof in your dashboard."
        )
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class PaymentProof(models.Model):
    PAYMENT_METHODS = [
        ("baridimob", "BaridiMob"),
        ("ccp_cheque", "CCP Cheque"),
        ("bank_transfer", "Bank Transfer"),
        ("cash_deposit", "Cash Deposit"),
        ("other", "Other"),
    ]

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payment_proofs"
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    proof_file = models.FileField(upload_to="payment_proofs/%Y/%m/")
    transaction_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    # Verification
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_payments",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Payment Proof for {self.invoice.invoice_number}"


class PaymentReceipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, related_name="receipt"
    )
    payment_proof = models.ForeignKey(
        PaymentProof, on_delete=models.CASCADE, related_name="receipts"
    )

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=20)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.receipt_number}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCP-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class ComplaintReason(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Complaint(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_review", "In Review"),
        ("awaiting_user", "Awaiting User Response"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    complaint_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="complaints"
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="complaints",
        null=True,
        blank=True,
    )

    reason = models.ForeignKey(ComplaintReason, on_delete=models.SET_NULL, null=True)
    custom_reason = models.CharField(max_length=200, blank=True)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")

    # Admin response
    admin_notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    handled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handled_complaints",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Complaint {self.complaint_number}"

    def save(self, *args, **kwargs):
        if not self.complaint_number:
            self.complaint_number = f"CMP-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="complaint_attachments/%Y/%m/")
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.complaint.complaint_number}"


class Refund(models.Model):
    STATUS_CHOICES = [
        ("refund_pending", "Refund Pending"),
        ("refund_approved", "Refund Approved"),
        ("refund_processing", "Refund Processing"),
        ("refund_completed", "Refund Completed"),
        ("refund_rejected", "Refund Rejected"),
    ]

    REFUND_METHODS = [
        ("baridimob", "BaridiMob"),
        ("ccp", "CCP"),
        ("bank_transfer", "Bank Transfer"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]

    refund_number = models.CharField(max_length=50, unique=True, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="refunds"
    )
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_method = models.CharField(max_length=20, choices=REFUND_METHODS, blank=True)
    reason = models.TextField()

    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="refund_pending"
    )

    # Admin
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_refunds",
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_refunds",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund {self.refund_number}"

    def save(self, *args, **kwargs):
        if not self.refund_number:
            self.refund_number = f"RFD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class RefundProof(models.Model):
    refund = models.OneToOneField(
        Refund, on_delete=models.CASCADE, related_name="proof"
    )
    proof_file = models.FileField(upload_to="refund_proofs/%Y/%m/")
    transaction_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund Proof for {self.refund.refund_number}"


class RefundReceipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    refund = models.OneToOneField(
        Refund, on_delete=models.CASCADE, related_name="receipt"
    )
    refund_proof = models.ForeignKey(
        RefundProof, on_delete=models.CASCADE, related_name="receipts"
    )

    amount_refunded = models.DecimalField(max_digits=10, decimal_places=2)
    refund_date = models.DateTimeField()
    refund_method = models.CharField(max_length=20)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund Receipt {self.receipt_number}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RFDRCP-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class Notification(models.Model):
    TYPE_CHOICES = [
        ("order_created", "Order Created"),
        ("invoice_created", "Invoice Created"),
        ("payment_submitted", "Payment Submitted"),
        ("payment_confirmed", "Payment Confirmed"),
        ("payment_rejected", "Payment Rejected"),
        ("complaint_created", "Complaint Created"),
        ("complaint_updated", "Complaint Updated"),
        ("complaint_resolved", "Complaint Resolved"),
        ("refund_initiated", "Refund Initiated"),
        ("refund_completed", "Refund Completed"),
        ("order_shipped", "Order Shipped"),
        ("order_delivered", "Order Delivered"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Related objects
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, null=True, blank=True
    )
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, null=True, blank=True
    )
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, null=True, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"
