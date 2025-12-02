from django import forms
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from .models import Profile
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))

class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label="Role",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")