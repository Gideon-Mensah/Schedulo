from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

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


