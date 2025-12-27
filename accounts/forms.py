from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, Div
from .models import UserProfile, PharmacyProfile, ClinicProfile, DoctorProfile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES, required=True)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Account Information",
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
                "Password",
                "password1",
                "password2",
            ),
            Submit(
                "submit", "Create Account", css_class="btn btn-primary btn-lg w-100"
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
            Submit("submit", "Update Profile", css_class="btn btn-primary"),
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
        widgets = {
            "license_expiry": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Pharmacy Information",
                "pharmacy_name",
                Row(
                    Column("license_number", css_class="form-group col-md-6 mb-3"),
                    Column("license_expiry", css_class="form-group col-md-6 mb-3"),
                ),
                "business_registration",
                "verification_documents",
            ),
            Submit("submit", "Update Pharmacy Profile", css_class="btn btn-primary"),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Clinic Information",
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
            Submit("submit", "Update Clinic Profile", css_class="btn btn-primary"),
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
        widgets = {
            "credentials": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Medical Information",
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
            Submit("submit", "Update Doctor Profile", css_class="btn btn-primary"),
        )

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
