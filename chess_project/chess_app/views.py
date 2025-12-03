import csv
import json
import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import Profile

from django.db.models import Avg, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import TaskResult


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
    file_path = os.path.join(settings.BASE_DIR, "chess_app", "data", "sample_task_batch.csv")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    return render(request, "student_dashboard.html", {"positions_json": json.dumps(rows)})


def trainer_dashboard(request):
    return render(request, "trainer_dashboard.html")


def dashboard(request):
    return render(request, "dashboard.html")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data["role"]
            profile.save()

            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


from django.http import JsonResponse

from .models import TaskResult

@csrf_exempt
def save_result(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)

        level = data.get("level")
        score = data.get("score")
        avg_time = data.get("avg_time")

        TaskResult.objects.create(user=request.user, level=level, score=score, avg_time=avg_time)

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)


def results_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    all_results = TaskResult.objects.filter(user=request.user).order_by('-created_at')

    if not all_results.exists():
        return render(request, "results.html", {"no_data": True})

    latest_result = all_results.first()

    total_stats = all_results.aggregate(
        total_games=Count('id'),
        avg_score=Avg('score'),
        avg_time=Avg('avg_time')
    )

    now = timezone.now()
    month_results = all_results.filter(created_at__year=now.year, created_at__month=now.month)
    month_avg = month_results.aggregate(avg_score=Avg('score'))['avg_score'] or 0

    global_avg = total_stats['avg_score'] or 0
    progress = month_avg - global_avg

    context = {
        "latest": latest_result,
        "total_games": total_stats['total_games'],
        "avg_score": round(global_avg, 2),
        "avg_time": round(total_stats['avg_time'], 1),
        "month_avg": round(month_avg, 2),
        "progress": round(progress, 2),
        "is_positive": progress >= 0
    }

    return render(request, "results.html", context)