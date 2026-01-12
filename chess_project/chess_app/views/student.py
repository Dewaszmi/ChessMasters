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

# student.py (views)
@login_required
@require_POST
def save_result(request):
    try:
        data = json.loads(request.body)
        module_id = data.get("module_id")
        tasks_data = data.get("tasks_data", [])
        module = get_object_or_404(Module, id=module_id)

        # 1. Save Task results
        for task_info in tasks_data:
            StudentTaskResult.objects.update_or_create(
                student=request.user, module=module, task_id=task_info['task_id'],
                defaults={'is_correct': task_info['is_correct'], 'user_move': task_info['user_move']}
            )

        # 2. Recalculate Score from all results in this module
        correct_count = StudentTaskResult.objects.filter(
            student=request.user, module=module, is_correct=True
        ).count()

        # 3. Update StudentModule and check for completion
        sm = get_object_or_404(StudentModule, student=request.user, module=module)
        sm.score = correct_count
        
        # Mark completed if user has attempted all tasks in the module
        if StudentTaskResult.objects.filter(student=request.user, module=module).count() >= module.tasks.count():
            sm.is_completed = True
        
        sm.save() # This triggers your trainer notification signal

        return JsonResponse({"status": "ok", "score": correct_count})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)