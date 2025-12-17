import json

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from ..models import Task, TaskResult


# helper decorator to check if user is authenticated and a student
def is_student(user):
    return user.is_authenticated and user.profile.role == "student"


student_required = user_passes_test(is_student)


@student_required
def student_dashboard(request):
    tasks_from_db = list(
        Task.objects.all().values("id", "fen", "correct_move", "level")
    )

    return render(
        request, "student_dashboard.html", {"positions_json": json.dumps(tasks_from_db)}
    )


@student_required
def dashboard(request):
    return render(request, "dashboard.html")


def save_result(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)

        level = data.get("level")
        score = data.get("score")
        avg_time = data.get("avg_time")

        TaskResult.objects.create(
            user=request.user, level=level, score=score, avg_time=avg_time
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)


def results_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    all_results = TaskResult.objects.filter(user=request.user).order_by("-created_at")

    if not all_results.exists():
        return render(request, "results.html", {"no_data": True})

    latest_result = all_results.first()

    total_stats = all_results.aggregate(
        total_games=Count("id"), avg_score=Avg("score"), avg_time=Avg("avg_time")
    )

    now = timezone.now()
    month_results = all_results.filter(
        created_at__year=now.year, created_at__month=now.month
    )
    month_avg = month_results.aggregate(avg_score=Avg("score"))["avg_score"] or 0

    global_avg = total_stats["avg_score"] or 0
    progress = month_avg - global_avg

    context = {
        "latest": latest_result,
        "total_games": total_stats["total_games"],
        "avg_score": round(global_avg, 2),
        "avg_time": round(total_stats["avg_time"], 1),
        "month_avg": round(month_avg, 2),
        "progress": round(progress, 2),
        "is_positive": progress >= 0,
    }

    return render(request, "results.html", context)
