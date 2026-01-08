import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..models import Module, StudentModule, Task, TaskResult, StudentTaskResult

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
    assigned_modules = StudentModule.objects.filter(student=request.user)
    total_assigned = assigned_modules.count()
    completed_count = assigned_modules.filter(is_completed=True).count()

    all_task_attempts = StudentTaskResult.objects.filter(student=request.user)
    total_tasks_attempted = all_task_attempts.count()
    correct_tasks = all_task_attempts.filter(is_correct=True).count()

    accuracy = (correct_tasks / total_tasks_attempted * 100) if total_tasks_attempted > 0 else 0

    recent_tasks = all_task_attempts.select_related('task', 'module').order_by('-timestamp')[:5]

    context = {
        "total_assigned": total_assigned,
        "completed_count": completed_count,
        "completion_rate": int((completed_count / total_assigned * 100)) if total_assigned > 0 else 0,
        "total_tasks": total_tasks_attempted,
        "accuracy": round(accuracy, 1),
        "recent_tasks": recent_tasks,
    }

    return render(request, "results.html", context)

@login_required
@require_POST
def save_result(request):
    try:
        data = json.loads(request.body)
        module_id = data.get("module_id")
        score = data.get("score")
        # To są dane o każdym zadaniu, które dodaliśmy w student.js
        tasks_data = data.get("tasks_data", [])

        module = get_object_or_404(Module, id=module_id)

        # 1. Aktualizujemy ogólny postęp w module
        student_module, created = StudentModule.objects.get_or_create(
            student=request.user,
            module=module
        )
        student_module.score = score
        student_module.is_completed = True
        student_module.save()

        # 2. Zapisujemy wyniki KAŻDEGO zadania z osobna
        for task_info in tasks_data:
            task = get_object_or_404(Task, id=task_info['task_id'])
            StudentTaskResult.objects.create(
                student=request.user,
                module=module,
                task=task,
                is_correct=task_info['is_correct'],
                user_move=task_info['user_move']
            )

        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)