from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nazwa użytkownika",
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Twój login"
        })
    )
    password = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Twoje hasło"
        })
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "jan@example.com"
        })
    )

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label="Rola",
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'