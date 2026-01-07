from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div
from .models import ProductReview, ProductQuestion


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "title", "comment"]
        labels = {
            "rating": "Note",
            "title": "Titre",
            "comment": "Commentaire",
        }
        widgets = {
            "rating": forms.Select(
                choices=[(i, f'{i} Étoile{"s" if i != 1 else ""}') for i in range(1, 6)]
            ),
            "comment": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("rating", css_class="form-group col-md-6 mb-3"),
                Column("title", css_class="form-group col-md-6 mb-3"),
            ),
            "comment",
            Submit("submit", "Soumettre l'avis", css_class="btn btn-primary"),
        )

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class ProductQuestionForm(forms.ModelForm):
    class Meta:
        model = ProductQuestion
        fields = ["question"]
        labels = {
            "question": "Question",
        }
        widgets = {
            "question": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Posez une question sur ce produit..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "question",
            Submit("submit", "Poser la question", css_class="btn btn-primary"),
        )

        self.fields["question"].widget.attrs.update({"class": "form-control"})


class ProductFilterForm(forms.Form):
    SORT_CHOICES = [
        ("name", "Nom A-Z"),
        ("price_low", "Prix : Croissant"),
        ("price_high", "Prix : Décroissant"),
        ("newest", "Plus récents"),
        ("rating", "Mieux notés"),
    ]

    category = forms.CharField(required=False, widget=forms.HiddenInput())
    brand = forms.CharField(required=False, widget=forms.HiddenInput())
    specialty = forms.CharField(required=False, widget=forms.HiddenInput())
    price_min = forms.DecimalField(
        required=False,
        label="Prix minimum",
        widget=forms.NumberInput(attrs={"placeholder": "Prix min"}),
    )
    price_max = forms.DecimalField(
        required=False,
        label="Prix maximum",
        widget=forms.NumberInput(attrs={"placeholder": "Prix max"}),
    )
    availability = forms.CharField(required=False, widget=forms.HiddenInput())
    sort = forms.ChoiceField(
        choices=SORT_CHOICES, required=False, initial="name", label="Trier par"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ["category", "brand", "specialty", "availability"]:
                self.fields[field].widget.attrs.update({"class": "form-control"})
