import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ..models import Module, StudentModule, Task, TaskResult



def is_student(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == "student"

student_required = user_passes_test(is_student)



@login_required
def student_dashboard(request):
    """Główny panel studenta - widzi tylko przypisane mu moduły."""

    assigned_relations = StudentModule.objects.filter(student=request.user).select_related('module').order_by('-module__created_at')

    modules_data = []
    for rel in assigned_relations:
        m = rel.module
        modules_data.append({
            'id': m.id,
            'title': m.title,
            'date': m.created_at.strftime("%d.%m.%Y"),
            'score': f"{rel.score} / {rel.max_score}",
            'is_completed': rel.is_completed
        })

    
    return render(request, "student_dashboard.html", {"modules": modules_data})


@login_required
def get_module_tasks(request, module_id):
    """Zwraca zadania JSON dla szachownicy."""

    if not StudentModule.objects.filter(student=request.user, module_id=module_id).exists():
        return JsonResponse({'error': 'Brak dostępu'}, status=403)
    
    module = get_object_or_404(Module, id=module_id)
    tasks = module.tasks.all()
    
    tasks_list = []
    for t in tasks:
        tasks_list.append({
            'id': t.id,
            'fen': t.fen,
            'solution': t.correct_move 
        })
        
    return JsonResponse(tasks_list, safe=False)



@login_required
def results_view(request):
    """Widok statystyk studenta (naprawia błąd AttributeError)."""
    all_results = TaskResult.objects.filter(user=request.user).order_by("-created_at")

    if not all_results.exists():
        return render(request, "student/results.html", {"no_data": True})

    latest_result = all_results.first()


    total_stats = all_results.aggregate(
        total_games=Count("id"), 
        avg_score=Avg("score"), 
        avg_time=Avg("avg_time")
    )

    now = timezone.now()
    month_results = all_results.filter(
        created_at__year=now.year, 
        created_at__month=now.month
    )
    month_avg = month_results.aggregate(avg_score=Avg("score"))["avg_score"] or 0

    global_avg = total_stats["avg_score"] or 0
    progress = month_avg - global_avg

    context = {
        "latest": latest_result,
        "total_games": total_stats["total_games"],
        "avg_score": round(global_avg, 2),
        "avg_time": round(total_stats["avg_time"] or 0, 1),
        "month_avg": round(month_avg, 2),
        "progress": round(progress, 2),
        "is_positive": progress >= 0,
    }

    return render(request, "student/results.html", context)



@csrf_exempt
@login_required
def save_result(request):
    """Zapisuje wynik po rozwiązaniu zadania (dobrym lub złym)."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            module_id = data.get('module_id')
            is_correct = data.get('is_correct')

           
            rel = get_object_or_404(StudentModule, student=request.user, module_id=module_id)

            if is_correct:
                rel.score += 1 
            
           
            if rel.score >= rel.max_score:
                rel.is_completed = True
            
            rel.save()
            return JsonResponse({"status": "ok", "new_score": rel.score})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error"}, status=405)