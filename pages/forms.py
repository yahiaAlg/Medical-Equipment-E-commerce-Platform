from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        labels = {
            "name": "Nom complet",
            "email": "Adresse e-mail",
            "phone": "Numéro de téléphone",
            "inquiry_type": "Type de demande",
            "subject": "Sujet",
            "message": "Votre message",
        }
        fields = ["name", "email", "phone", "inquiry_type", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nom complet"}),
            "email": forms.EmailInput(attrs={"placeholder": "Adresse e-mail"}),
            "phone": forms.TextInput(attrs={"placeholder": "Numéro de téléphone"}),
            "subject": forms.TextInput(attrs={"placeholder": "Sujet"}),
            "message": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Votre message"}
            ),
            "inquiry_type": forms.Select(
                attrs={"placeholder": "Type de demande", "class": "form-select"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group col-md-6 mb-3"),
                Column("email", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("phone", css_class="form-group col-md-6 mb-3"),
                Column("inquiry_type", css_class="form-group col-md-6 mb-3"),
            ),
            "subject",
            "message",
            Submit("submit", "Envoyer le message", css_class="btn btn-primary btn-lg"),
        )

        # Add Bootstrap classes
        for field in self.fields:
            if field != "inquiry_type":
                self.fields[field].widget.attrs.update({"class": "form-control"})
