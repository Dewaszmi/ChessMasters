from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from ..forms import LoginForm, RegisterForm
from ..models import Group, Profile, Task, TaskResult


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile = Profile.objects.get(user=user)
            if profile.role == "student":
                return redirect("student_dashboard")
            else:
                # ZMIENIONO Z trainer_dashboard NA trainer_home
                return redirect("trainer_home")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data["role"]
            profile.save()

            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})