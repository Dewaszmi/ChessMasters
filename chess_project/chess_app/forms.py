from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import Module

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

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        if not password:
            raise forms.ValidationError("Hasło nie może być puste")

        if len(password) < 3:
            raise forms.ValidationError("Hasło musi mieć co najmniej 3 znaki")

        return password

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title", "tasks"]
        labels = {"title": "Nazwa modułu", "tasks": "Zadania w module"}
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "tasks": forms.SelectMultiple(attrs={"class": "form-select", "size": "10"}),
        }