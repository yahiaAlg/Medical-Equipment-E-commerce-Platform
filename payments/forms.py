from django import forms
from .models import (
    PaymentProof,
    Complaint,
    ComplaintAttachment,
    RefundProof,
    ComplaintReason,
    ShippingType,
)


class CheckoutForm(forms.Form):
    shipping_type = forms.ModelChoiceField(
        queryset=ShippingType.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Méthode de livraison",
    )

    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        label="Adresse de livraison",
    )
    shipping_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Ville",
    )
    shipping_state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Wilaya",
    )
    shipping_zip = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Code postal",
    )

    billing_same = forms.BooleanField(
        required=False,
        initial=True,
        label="L'adresse de facturation est la même que l'adresse de livraison",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    order_note = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "Instructions de livraison spéciales, exigences médicales, etc.",
            }
        ),
        label="Notes de commande (facultatif)",
    )


class PaymentProofUploadForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = ["payment_method", "proof_file", "transaction_reference", "notes"]
        widgets = {
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "proof_file": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*,application/pdf"}
            ),
            "transaction_reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ID ou référence de transaction",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notes facultatives concernant votre paiement",
                }
            ),
        }
        labels = {
            "payment_method": "Méthode de paiement",
            "proof_file": "Télécharger la preuve de paiement (Image ou PDF)",
            "transaction_reference": "Référence de transaction",
            "notes": "Notes supplémentaires",
        }

    def clean_proof_file(self):
        file = self.cleaned_data.get("proof_file")
        if file:
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "La taille du fichier doit être inférieure à 5 Mo."
                )

            allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
            if file.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Seuls les fichiers JPG, PNG et PDF sont autorisés."
                )
        return file


class PaymentVerificationForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ("approve", "Approuver le paiement"),
            ("reject", "Rejeter le paiement"),
        ],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Action",
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Motif du rejet",
            }
        ),
        label="Motif du rejet (si rejeté)",
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        rejection_reason = cleaned_data.get("rejection_reason")

        if action == "reject" and not rejection_reason:
            raise forms.ValidationError(
                "Le motif du rejet est obligatoire lors du rejet d'un paiement."
            )

        return cleaned_data


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["reason", "custom_reason", "description"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-select"}),
            "custom_reason": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Précisez si vous avez sélectionné « Autre »",
                    "id": "custom_reason_field",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Veuillez décrire votre réclamation en détail...",
                }
            ),
        }
        labels = {
            "reason": "Motif de la réclamation",
            "custom_reason": "Motif personnalisé",
            "description": "Description",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reason"].queryset = ComplaintReason.objects.filter(is_active=True)
        self.fields["reason"].empty_label = "Sélectionnez un motif"


class ComplaintAttachmentForm(forms.ModelForm):
    class Meta:
        model = ComplaintAttachment
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*,video/*,application/pdf",
                }
            ),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    "La taille du fichier doit être inférieure à 10 Mo."
                )

            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/jpg",
                "image/gif",
                "video/mp4",
                "video/quicktime",
                "application/pdf",
            ]
            if file.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Seuls les images, vidéos (MP4) et fichiers PDF sont autorisés."
                )
        return file


class ComplaintReasonForm(forms.ModelForm):
    class Meta:
        model = ComplaintReason
        fields = ["name", "description", "is_active", "display_order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "display_order": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Nom",
            "description": "Description",
            "is_active": "Actif",
            "display_order": "Ordre d'affichage",
        }


class ComplaintStatusUpdateForm(forms.Form):
    STATUS_CHOICES = [
        ("in_review", "En cours d'examen"),
        ("awaiting_user", "En attente de réponse du client"),
        ("resolved", "Résolue"),
        ("rejected", "Rejetée"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Nouveau statut",
    )
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        label="Notes administrateur",
        required=False,
    )
    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        label="Notes de résolution",
        required=False,
    )


class RefundInitiationForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        label="Montant du remboursement",
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        label="Motif du remboursement",
    )


class RefundProofUploadForm(forms.ModelForm):
    refund_method = forms.ChoiceField(
        choices=[
            (m[0], m[1])
            for m in [
                ("baridimob", "BaridiMob"),
                ("ccp", "CCP"),
                ("bank_transfer", "Virement bancaire"),
                ("cash", "Espèces"),
                ("other", "Autre"),
            ]
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Méthode de remboursement",
    )

    class Meta:
        model = RefundProof
        fields = ["proof_file", "transaction_reference", "notes"]
        widgets = {
            "proof_file": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*,application/pdf"}
            ),
            "transaction_reference": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "proof_file": "Preuve de remboursement",
            "transaction_reference": "Référence de transaction",
            "notes": "Notes",
        }

    def clean_proof_file(self):
        file = self.cleaned_data.get("proof_file")
        if file:
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "La taille du fichier doit être inférieure à 5 Mo."
                )

            allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
            if file.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Seuls les fichiers JPG, PNG et PDF sont autorisés."
                )
        return file


from .models import OrderNote, OrderNoteAttachment, ShippingType


class OrderNoteForm(forms.ModelForm):
    class Meta:
        model = OrderNote
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Ajouter des notes concernant cette commande...",
                }
            )
        }
        labels = {"content": "Notes de commande"}


class OrderNoteAttachmentForm(forms.ModelForm):
    class Meta:
        model = OrderNoteAttachment
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*,application/pdf,.doc,.docx",
                }
            )
        }
        labels = {"file": "Fichier"}

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    "La taille du fichier doit être inférieure à 10 Mo."
                )

            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/jpg",
                "image/gif",
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ]
            if file.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Seuls les images, PDF et documents Word sont autorisés."
                )
        return file


class OrderConfirmationForm(forms.Form):
    ACTION_CHOICES = [
        ("confirm", "Confirmer la commande"),
        ("reject", "Rejeter la commande"),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Action",
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Ajouter des notes de confirmation/rejet...",
            }
        ),
        label="Notes",
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Obligatoire si rejet de la commande",
            }
        ),
        label="Motif du rejet",
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        rejection_reason = cleaned_data.get("rejection_reason")

        if action == "reject" and not rejection_reason:
            raise forms.ValidationError(
                "Le motif du rejet est obligatoire lors du rejet d'une commande."
            )

        return cleaned_data


class ShippingTypeForm(forms.ModelForm):
    class Meta:
        model = ShippingType
        fields = [
            "name",
            "description",
            "estimated_days",
            "cost",
            "is_active",
            "display_order",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "estimated_days": forms.NumberInput(attrs={"class": "form-control"}),
            "cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "display_order": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Nom",
            "description": "Description",
            "estimated_days": "Délai estimé (jours)",
            "cost": "Coût",
            "is_active": "Actif",
            "display_order": "Ordre d'affichage",
        }
