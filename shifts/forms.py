# shifts/forms.py
from django import forms
from .models import Shift

from django import forms
from django.contrib.auth import get_user_model
from .models import ComplianceDocument, ComplianceDocType

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = [
            "title", "date", "start_time", "end_time",
            "role", "location", "max_staff", "allowed_postcode",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Morning Care Shift"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Site / Address"}),
            "max_staff": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "allowed_postcode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. SW1A 1AA (optional)"
            }),
        }

    def clean_allowed_postcode(self):
        pc = self.cleaned_data.get("allowed_postcode") or ""
        pc = pc.upper().replace(" ", "")
        return pc or None

User = get_user_model()

class AdminUserCreateForm(forms.ModelForm):
    """
    Admin creates a user. Password is optional; if left blank we auto-generate one.
    """
    password = forms.CharField(
        required=False, widget=forms.PasswordInput, help_text="Leave blank to auto-generate a temporary password."
    )
    confirm_password = forms.CharField(
        required=False, widget=forms.PasswordInput, help_text="Repeat the password if you typed one."
    )

    class Meta:
        model = User
        # Adjust fields to match your custom user model:
        fields = ["username", "email", "first_name", "last_name", "is_staff", "is_active"]
        widgets = {
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        data = super().clean()
        p1 = data.get("password") or ""
        p2 = data.get("confirm_password") or ""
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match.")
            if len(p1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters.")
        return data
    
#Compliance forms

class AdminComplianceUploadForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Assign to user")

    class Meta:
        model = ComplianceDocument
        fields = ["user", "doc_type", "file", "issue_date", "expiry_date", "status", "notes"]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        dtype: ComplianceDocType = cleaned.get("doc_type")
        expiry = cleaned.get("expiry_date")

        if dtype and dtype.requires_expiry and not expiry:
            self.add_error("expiry_date", "This document type requires an expiry date.")
        return cleaned