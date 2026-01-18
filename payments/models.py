from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import uuid


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        return f"Panier de {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product", "variant")
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"

    def __str__(self):
        variant_info = f" ({self.variant.variant_value})" if self.variant else ""
        return f"{self.quantity} x {self.product.name}{variant_info}"

    def get_unit_price(self):
        """Get the price per item based on variant or product"""
        if self.variant:
            return self.variant.get_total_price()
        return self.product.price

    def get_total_price(self):
        """Get total price for this cart item"""
        return self.quantity * self.get_unit_price()


class ShippingType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    estimated_days = models.PositiveIntegerField(
        help_text="Délai de livraison estimé en jours"
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Coût")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    display_order = models.PositiveIntegerField(
        default=0, verbose_name="Ordre d'affichage"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Type de livraison"
        verbose_name_plural = "Types de livraison"

    def __str__(self):
        return f"{self.name} - {self.cost} DZD ({self.estimated_days} jours)"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending_confirmation", "En attente de confirmation"),
        ("confirmed", "Confirmée"),
        ("rejected", "Rejetée"),
        ("awaiting_payment", "En attente de paiement"),
        ("payment_under_review", "Paiement en cours de vérification"),
        ("paid", "Payée"),
        ("processing", "En traitement"),
        ("shipped", "Expédiée"),
        ("delivered", "Livrée"),
        ("cancelled", "Annulée"),
        ("refund_pending", "Remboursement en attente"),
        ("refunded", "Remboursée"),
    ]

    order_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending_confirmation",
        verbose_name="Statut",
    )

    shipping_type = models.ForeignKey(
        ShippingType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Type de livraison",
    )
    shipping_address = models.TextField(verbose_name="Adresse de livraison")
    shipping_city = models.CharField(max_length=100, verbose_name="Ville")
    shipping_state = models.CharField(max_length=100, verbose_name="Wilaya")
    shipping_zip = models.CharField(max_length=10, verbose_name="Code postal")
    shipping_country = models.CharField(
        max_length=100, default="Algérie", verbose_name="Pays"
    )

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Sous-total"
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Montant TVA"
    )
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Frais de livraison"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant total"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Confirmée le"
    )
    rejected_at = models.DateTimeField(blank=True, null=True, verbose_name="Rejetée le")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="Payée le")
    shipped_at = models.DateTimeField(blank=True, null=True, verbose_name="Expédiée le")
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name="Livrée le")

    tracking_number = models.CharField(
        max_length=100, blank=True, verbose_name="Numéro de suivi"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        return f"Commande {self.order_id}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"CMD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def can_update_status(self):
        """Vérifier si le statut de la commande peut être mis à jour"""
        return self.status not in ["pending_confirmation", "rejected"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Produit"
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Variante",
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        variant_info = f" ({self.variant.variant_value})" if self.variant else ""
        return f"{self.quantity} x {self.product.name}{variant_info}"

    def get_total_price(self):
        return self.quantity * self.price


class OrderNote(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="note")
    content = models.TextField(verbose_name="Contenu")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Créée par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Note de commande"
        verbose_name_plural = "Notes de commande"

    def __str__(self):
        return f"Note pour {self.order.order_id}"


class OrderNoteAttachment(models.Model):
    order_note = models.ForeignKey(
        OrderNote, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="order_notes/%Y/%m/", verbose_name="Fichier")
    file_name = models.CharField(max_length=255, verbose_name="Nom du fichier")
    file_type = models.CharField(max_length=50, verbose_name="Type de fichier")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe de note"
        verbose_name_plural = "Pièces jointes de notes"

    def __str__(self):
        return f"Pièce jointe pour {self.order_note.order.order_id}"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Impayée"),
        ("payment_submitted", "Paiement soumis"),
        ("payment_rejected", "Paiement rejeté"),
        ("paid", "Payée"),
        ("refunded", "Remboursée"),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="invoice"
    )
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="unpaid", verbose_name="Statut"
    )

    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Sous-total"
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Montant TVA"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant total"
    )

    payment_instructions = models.TextField(
        default=(
            "Veuillez effectuer le paiement via l'une des méthodes suivantes :\n"
            "1. BaridiMob : +213 XXX XXX XXX\n"
            "2. CCP : XXXXXX Clé XX\n"
            "3. Virement bancaire : IBAN DZXX XXXX XXXX XXXX XXXX\n"
            "Après paiement, téléchargez votre preuve dans votre tableau de bord."
        ),
        verbose_name="Instructions de paiement",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="Payée le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        return f"Facture {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"FACT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class PaymentProof(models.Model):
    PAYMENT_METHODS = [
        ("baridimob", "BaridiMob"),
        ("ccp_cheque", "Chèque CCP"),
        ("bank_transfer", "Virement bancaire"),
        ("cash_deposit", "Dépôt en espèces"),
        ("other", "Autre"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payment_proofs",
        verbose_name="Facture",
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, verbose_name="Méthode de paiement"
    )
    proof_file = models.FileField(
        upload_to="payment_proofs/%Y/%m/", verbose_name="Preuve de paiement"
    )
    transaction_reference = models.CharField(
        max_length=100, blank=True, verbose_name="Référence de transaction"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")

    verified = models.BooleanField(default=False, verbose_name="Vérifié")
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_payments",
        verbose_name="Vérifié par",
    )
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name="Vérifié le")
    rejection_reason = models.TextField(blank=True, verbose_name="Motif de rejet")

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Preuve de paiement"
        verbose_name_plural = "Preuves de paiement"

    def __str__(self):
        return f"Preuve de paiement pour {self.invoice.invoice_number}"


class PaymentReceipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE, related_name="receipt"
    )
    payment_proof = models.ForeignKey(
        PaymentProof, on_delete=models.CASCADE, related_name="receipts"
    )

    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant payé"
    )
    payment_date = models.DateTimeField(verbose_name="Date de paiement")
    payment_method = models.CharField(max_length=20, verbose_name="Méthode de paiement")

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reçu de paiement"
        verbose_name_plural = "Reçus de paiement"

    def __str__(self):
        return f"Reçu {self.receipt_number}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RECU-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class ComplaintReason(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    display_order = models.PositiveIntegerField(
        default=0, verbose_name="Ordre d'affichage"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Motif de réclamation"
        verbose_name_plural = "Motifs de réclamation"

    def __str__(self):
        return self.name


class Complaint(models.Model):
    STATUS_CHOICES = [
        ("open", "Ouverte"),
        ("in_review", "En cours d'examen"),
        ("awaiting_user", "En attente de réponse du client"),
        ("resolved", "Résolue"),
        ("rejected", "Rejetée"),
    ]

    complaint_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints",
        verbose_name="Utilisateur",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="complaints",
        verbose_name="Commande",
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="complaints",
        null=True,
        blank=True,
        verbose_name="Facture",
    )

    reason = models.ForeignKey(
        ComplaintReason, on_delete=models.SET_NULL, null=True, verbose_name="Motif"
    )
    custom_reason = models.CharField(
        max_length=200, blank=True, verbose_name="Motif personnalisé"
    )
    description = models.TextField(verbose_name="Description")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open", verbose_name="Statut"
    )

    admin_notes = models.TextField(blank=True, verbose_name="Notes administrateur")
    resolution_notes = models.TextField(blank=True, verbose_name="Notes de résolution")
    handled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handled_complaints",
        verbose_name="Traitée par",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name="Résolue le")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Réclamation"
        verbose_name_plural = "Réclamations"

    def __str__(self):
        return f"Réclamation {self.complaint_number}"

    def save(self, *args, **kwargs):
        if not self.complaint_number:
            self.complaint_number = f"RECL-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class ComplaintAttachment(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(
        upload_to="complaint_attachments/%Y/%m/", verbose_name="Fichier"
    )
    file_type = models.CharField(max_length=50, verbose_name="Type de fichier")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe de réclamation"
        verbose_name_plural = "Pièces jointes de réclamations"

    def __str__(self):
        return f"Pièce jointe pour {self.complaint.complaint_number}"


class Refund(models.Model):
    STATUS_CHOICES = [
        ("refund_pending", "Remboursement en attente"),
        ("refund_approved", "Remboursement approuvé"),
        ("refund_processing", "Remboursement en cours"),
        ("refund_completed", "Remboursement effectué"),
        ("refund_rejected", "Remboursement rejeté"),
    ]

    REFUND_METHODS = [
        ("baridimob", "BaridiMob"),
        ("ccp", "CCP"),
        ("bank_transfer", "Virement bancaire"),
        ("cash", "Espèces"),
        ("other", "Autre"),
    ]

    refund_number = models.CharField(max_length=50, unique=True, editable=False)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="refunds", verbose_name="Commande"
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="refunds",
        verbose_name="Facture",
    )
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunds",
        verbose_name="Réclamation",
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant"
    )
    refund_method = models.CharField(
        max_length=20,
        choices=REFUND_METHODS,
        blank=True,
        verbose_name="Méthode de remboursement",
    )
    reason = models.TextField(verbose_name="Motif")

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="refund_pending",
        verbose_name="Statut",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_refunds",
        verbose_name="Approuvé par",
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_refunds",
        verbose_name="Traité par",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Approuvé le"
    )
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name="Traité le")
    completed_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Effectué le"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Remboursement"
        verbose_name_plural = "Remboursements"

    def __str__(self):
        return f"Remboursement {self.refund_number}"

    def save(self, *args, **kwargs):
        if not self.refund_number:
            self.refund_number = f"REMB-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class RefundProof(models.Model):
    refund = models.OneToOneField(
        Refund, on_delete=models.CASCADE, related_name="proof"
    )
    proof_file = models.FileField(
        upload_to="refund_proofs/%Y/%m/", verbose_name="Preuve de remboursement"
    )
    transaction_reference = models.CharField(
        max_length=100, blank=True, verbose_name="Référence de transaction"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Téléchargé par"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Preuve de remboursement"
        verbose_name_plural = "Preuves de remboursement"

    def __str__(self):
        return f"Preuve de remboursement pour {self.refund.refund_number}"


class RefundReceipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    refund = models.OneToOneField(
        Refund, on_delete=models.CASCADE, related_name="receipt"
    )
    refund_proof = models.ForeignKey(
        RefundProof, on_delete=models.CASCADE, related_name="receipts"
    )

    amount_refunded = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant remboursé"
    )
    refund_date = models.DateTimeField(verbose_name="Date de remboursement")
    refund_method = models.CharField(
        max_length=20, verbose_name="Méthode de remboursement"
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reçu de remboursement"
        verbose_name_plural = "Reçus de remboursement"

    def __str__(self):
        return f"Reçu de remboursement {self.receipt_number}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RECUREMB-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class Notification(models.Model):
    TYPE_CHOICES = [
        ("order_created", "Commande créée"),
        ("invoice_created", "Facture créée"),
        ("payment_submitted", "Paiement soumis"),
        ("payment_confirmed", "Paiement confirmé"),
        ("payment_rejected", "Paiement rejeté"),
        ("complaint_created", "Réclamation créée"),
        ("complaint_updated", "Réclamation mise à jour"),
        ("complaint_resolved", "Réclamation résolue"),
        ("refund_initiated", "Remboursement initié"),
        ("refund_completed", "Remboursement effectué"),
        ("order_shipped", "Commande expédiée"),
        ("order_delivered", "Commande livrée"),
        ("order_confirmed", "Commande confirmée"),
        ("order_rejected", "Commande rejetée"),
        ("user_registered", "Nouvel utilisateur inscrit"),
        ("review_submitted", "Nouvel avis soumis"),
        ("question_submitted", "Nouvelle question soumise"),
        ("contact_message", "Nouveau message de contact"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Utilisateur",
    )
    notification_type = models.CharField(
        max_length=30, choices=TYPE_CHOICES, verbose_name="Type de notification"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Commande"
    )
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Facture"
    )
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Réclamation",
    )
    refund = models.ForeignKey(
        Refund,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Remboursement",
    )

    related_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications_about",
        verbose_name="Utilisateur concerné",
    )
    review_id = models.IntegerField(null=True, blank=True, verbose_name="ID de l'avis")
    question_id = models.IntegerField(
        null=True, blank=True, verbose_name="ID de la question"
    )
    contact_id = models.IntegerField(
        null=True, blank=True, verbose_name="ID du contact"
    )

    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"
