from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.urls import reverse_lazy
from .models import User, IDCard

class UserRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

# forms.py (for AuthenticationForm or your custom form)
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control form-control-lg'})
            
# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "phone", "job_title", "bio"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

class CustomPasswordResetForm(SetPasswordForm):
    """
    Custom form that only requires new password and confirmation,
    without asking for the old password
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to the form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Customize field labels and help text
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'
        self.fields['new_password1'].help_text = (
            'Your password must contain at least 8 characters and cannot be entirely numeric.'
        )


class IDCardForm(forms.ModelForm):
    """Form for creating and updating ID cards with AJAX-powered searchable employee selection."""
    
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Empty queryset for AJAX loading
        widget=forms.Select(attrs={
            "class": "form-control",
            "data-ajax--url": reverse_lazy("accounts:employee_search"),
            "data-placeholder": "Search and select an employee...",
        }),
        help_text="Start typing to search for employees by name, username, or email"
    )
    
    class Meta:
        model = IDCard
        fields = ['user', 'department', 'expiry_date', 'emergency_contact_name', 'emergency_contact_phone', 'access_level']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'access_level': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract organization and request from kwargs if provided
        self.organization = kwargs.pop('organization', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Ensure the selected user is available to the field (for editing or POST back)
        selected_id = None
        if self.data.get("user"):
            selected_id = self.data.get("user")
        elif getattr(self.instance, "user_id", None):
            selected_id = self.instance.user_id

        if selected_id:
            # Load only the selected user for the queryset
            if self.organization:
                self.fields["user"].queryset = User.objects.filter(
                    pk=selected_id,
                    profile__organization=self.organization
                )
            else:
                self.fields["user"].queryset = User.objects.filter(pk=selected_id)
        else:
            self.fields["user"].queryset = User.objects.none()
        
        # Add better help text
        self.fields['department'].help_text = "Employee's department or division"
        self.fields['expiry_date'].help_text = "When this ID card expires (optional)"
        self.fields['emergency_contact_name'].help_text = "Emergency contact full name"
        self.fields['emergency_contact_phone'].help_text = "Emergency contact phone number"
        self.fields['access_level'].help_text = "Access permissions level"


