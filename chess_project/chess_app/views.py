from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from .forms import LoginForm
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
    return render(request, "student_dashboard.html")


def trainer_dashboard(request):
    return render(request, "trainer_dashboard.html")

def dashboard(request):
    return render(request, "dashboard.html")