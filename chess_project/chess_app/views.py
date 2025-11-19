from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import Profile


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
                return redirect("trainer_dashboard")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def student_dashboard(request):
    fen = "rnbqkbnr/ppp2ppp/8/3pp3/8/2N5/PPPPPPPP/R1BQKBNR w KQkq - 0 1"
    return render(request, "student_dashboard.html", {"initial_fen": fen})


def trainer_dashboard(request):
    return render(request, "trainer_dashboard.html")


def dashboard(request):
    return render(request, "dashboard.html")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data.get("email", "") or "",
                password=form.cleaned_data["password"],
            )
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})
