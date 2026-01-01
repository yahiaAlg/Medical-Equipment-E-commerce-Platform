from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        labels = {
            "name": "Full Name",
            "email": "Email Address",
            "phone": "Phone Number",
            "inquiry_type": "Type of Inquiry",
            "subject": "Subject",
            "message": "Your Message",
        }
        fields = ["name", "email", "phone", "inquiry_type", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email Address"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone Number"}),
            "subject": forms.TextInput(attrs={"placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Your Message"}),
            "inquiry_type": forms.Select(
                attrs={"placeholder": "Type of Inquiry", "class": "form-select"}
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
            Submit("submit", "Send Message", css_class="btn btn-primary btn-lg"),
        )

        # Add Bootstrap classes
        for field in self.fields:
            if field != "inquiry_type":
                self.fields[field].widget.attrs.update({"class": "form-control"})
