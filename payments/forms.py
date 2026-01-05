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
    # Shipping Type
    shipping_type = forms.ModelChoiceField(
        queryset=ShippingType.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Shipping Method",
    )

    # Shipping Information
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        label="Shipping Address",
    )
    shipping_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="City",
    )
    shipping_state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="State/Province",
    )
    shipping_zip = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="ZIP Code",
    )

    # Billing same as shipping
    billing_same = forms.BooleanField(
        required=False,
        initial=True,
        label="Billing address is the same as shipping address",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    # Order Notes
    order_note = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "Special delivery instructions, medical requirements, etc.",
            }
        ),
        label="Order Notes (Optional)",
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
                    "placeholder": "Transaction ID or Reference",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional notes about your payment",
                }
            ),
        }
        labels = {
            "payment_method": "Payment Method",
            "proof_file": "Upload Payment Proof (Image or PDF)",
            "transaction_reference": "Transaction Reference",
            "notes": "Additional Notes",
        }

    def clean_proof_file(self):
        file = self.cleaned_data.get("proof_file")
        if file:
            # Validate file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5MB.")

            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Only JPG, PNG, and PDF files are allowed.")
        return file


class PaymentVerificationForm(forms.Form):
    action = forms.ChoiceField(
        choices=[("approve", "Approve Payment"), ("reject", "Reject Payment")],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Action",
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Reason for rejection",
            }
        ),
        label="Rejection Reason (if rejecting)",
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        rejection_reason = cleaned_data.get("rejection_reason")

        if action == "reject" and not rejection_reason:
            raise forms.ValidationError(
                "Rejection reason is required when rejecting a payment."
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
                    "placeholder": 'Specify if you selected "Other"',
                    "id": "custom_reason_field",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Please describe your complaint in detail...",
                }
            ),
        }
        labels = {
            "reason": "Complaint Reason",
            "custom_reason": "Custom Reason",
            "description": "Description",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reason"].queryset = ComplaintReason.objects.filter(is_active=True)
        self.fields["reason"].empty_label = "Select a reason"


class ComplaintAttachmentForm(forms.ModelForm):
    class Meta:
        model = ComplaintAttachment
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*,video/*,application/pdf",
                    # "multiple": True,
                }
            ),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            # Max 10MB per file
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB.")

            # Allowed types
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
                    "Only images, videos (MP4), and PDF files are allowed."
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


class ComplaintStatusUpdateForm(forms.Form):
    STATUS_CHOICES = [
        ("in_review", "In Review"),
        ("awaiting_user", "Awaiting User Response"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="New Status",
    )
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        label="Admin Notes",
        required=False,
    )
    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        label="Resolution Notes",
        required=False,
    )


class RefundInitiationForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        label="Refund Amount",
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        label="Refund Reason",
    )


class RefundProofUploadForm(forms.ModelForm):
    refund_method = forms.ChoiceField(
        choices=[
            (m[0], m[1])
            for m in [
                ("baridimob", "BaridiMob"),
                ("ccp", "CCP"),
                ("bank_transfer", "Bank Transfer"),
                ("cash", "Cash"),
                ("other", "Other"),
            ]
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Refund Method",
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

    def clean_proof_file(self):
        file = self.cleaned_data.get("proof_file")
        if file:
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5MB.")

            allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Only JPG, PNG, and PDF files are allowed.")
        return file


# Add to payments/forms.py

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
                    "placeholder": "Add notes about this order...",
                }
            )
        }
        labels = {"content": "Order Notes"}


class OrderNoteAttachmentForm(forms.ModelForm):
    class Meta:
        model = OrderNoteAttachment
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*,application/pdf,.doc,.docx",
                    # "multiple": True,
                }
            )
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            # Max 10MB per file
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB.")

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
                    "Only images, PDF, and Word documents are allowed."
                )
        return file


class OrderConfirmationForm(forms.Form):
    ACTION_CHOICES = [("confirm", "Confirm Order"), ("reject", "Reject Order")]

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
                "placeholder": "Add confirmation/rejection notes...",
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
                "placeholder": "Required if rejecting order",
            }
        ),
        label="Rejection Reason",
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        rejection_reason = cleaned_data.get("rejection_reason")

        if action == "reject" and not rejection_reason:
            raise forms.ValidationError(
                "Rejection reason is required when rejecting an order."
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
