from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, Div

from products.models import ProductReview
from .models import UserProfile, PharmacyProfile, ClinicProfile, DoctorProfile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPES, required=True, label="Type d'utilisateur"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "user_type",
        )
        labels = {
            "username": "Nom d'utilisateur",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmer le mot de passe"

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Informations du compte",
                Row(
                    Column("first_name", css_class="form-group col-md-6 mb-3"),
                    Column("last_name", css_class="form-group col-md-6 mb-3"),
                ),
                Row(
                    Column("username", css_class="form-group col-md-6 mb-3"),
                    Column("email", css_class="form-group col-md-6 mb-3"),
                ),
                "user_type",
            ),
            Fieldset(
                "Mot de passe",
                "password1",
                "password2",
            ),
            Submit(
                "submit", "Créer un compte", css_class="btn btn-primary btn-lg w-100"
            ),
        )

        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Email",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class UserProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "avatar",
            "date_of_birth",
        ]
        labels = {
            "phone": "Téléphone",
            "address": "Adresse",
            "city": "Ville",
            "state": "État/Province",
            "zip_code": "Code postal",
            "country": "Pays",
            "avatar": "Photo de profil",
            "date_of_birth": "Date de naissance",
        }
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("phone", css_class="form-group col-md-6 mb-3"),
                Column("date_of_birth", css_class="form-group col-md-6 mb-3"),
            ),
            "address",
            Row(
                Column("city", css_class="form-group col-md-4 mb-3"),
                Column("state", css_class="form-group col-md-4 mb-3"),
                Column("zip_code", css_class="form-group col-md-4 mb-3"),
            ),
            "country",
            "avatar",
            Submit("submit", "Mettre à jour le profil", css_class="btn btn-primary"),
        )

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class PharmacyProfileForm(forms.ModelForm):
    class Meta:
        model = PharmacyProfile
        fields = [
            "pharmacy_name",
            "license_number",
            "license_expiry",
            "business_registration",
            "verification_documents",
        ]
        labels = {
            "pharmacy_name": "Nom de la pharmacie",
            "license_number": "Numéro de licence",
            "license_expiry": "Date d'expiration de la licence",
            "business_registration": "Numéro d'enregistrement commercial",
            "verification_documents": "Documents de vérification",
        }
        widgets = {
            "license_expiry": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Informations de la pharmacie",
                "pharmacy_name",
                Row(
                    Column("license_number", css_class="form-group col-md-6 mb-3"),
                    Column("license_expiry", css_class="form-group col-md-6 mb-3"),
                ),
                "business_registration",
                "verification_documents",
            ),
            Submit(
                "submit",
                "Mettre à jour le profil pharmacie",
                css_class="btn btn-primary",
            ),
        )

        for field in self.fields:
            if field != "verification_documents":
                self.fields[field].widget.attrs.update({"class": "form-control"})


class ClinicProfileForm(forms.ModelForm):
    class Meta:
        model = ClinicProfile
        fields = [
            "clinic_name",
            "department",
            "employee_id",
            "position",
            "supervisor_email",
            "budget_limit",
        ]
        labels = {
            "clinic_name": "Nom de la clinique",
            "department": "Département",
            "employee_id": "Identifiant employé",
            "position": "Poste",
            "supervisor_email": "Email du superviseur",
            "budget_limit": "Limite budgétaire",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Informations de la clinique",
                "clinic_name",
                Row(
                    Column("department", css_class="form-group col-md-6 mb-3"),
                    Column("position", css_class="form-group col-md-6 mb-3"),
                ),
                Row(
                    Column("employee_id", css_class="form-group col-md-6 mb-3"),
                    Column("supervisor_email", css_class="form-group col-md-6 mb-3"),
                ),
                "budget_limit",
            ),
            Submit(
                "submit",
                "Mettre à jour le profil clinique",
                css_class="btn btn-primary",
            ),
        )

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            "medical_license",
            "specialty",
            "years_of_experience",
            "hospital_affiliation",
            "credentials",
        ]
        labels = {
            "medical_license": "Numéro de licence médicale",
            "specialty": "Spécialité",
            "years_of_experience": "Années d'expérience",
            "hospital_affiliation": "Hôpital d'affiliation",
            "credentials": "Diplômes et certifications",
        }
        widgets = {
            "credentials": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Informations médicales",
                Row(
                    Column("medical_license", css_class="form-group col-md-6 mb-3"),
                    Column("specialty", css_class="form-group col-md-6 mb-3"),
                ),
                Row(
                    Column("years_of_experience", css_class="form-group col-md-6 mb-3"),
                    Column(
                        "hospital_affiliation", css_class="form-group col-md-6 mb-3"
                    ),
                ),
                "credentials",
            ),
            Submit(
                "submit", "Mettre à jour le profil médecin", css_class="btn btn-primary"
            ),
        )

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class ContactReplyForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        label="Objet",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6}),
    )


class QuestionReplyForm(forms.Form):
    answer = forms.CharField(
        label="Réponse",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Saisissez votre réponse...",
            }
        ),
    )


class ReviewReplyForm(forms.ModelForm):
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
                choices=[(i, f'{i} étoile{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={"class": "form-control"},
            ),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Titre de la réponse"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Votre réponse...",
                }
            ),
        }
