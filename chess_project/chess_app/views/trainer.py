import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import ModuleForm, TaskForm
from ..models import (
    Group,
    Module,
    Profile,
    StudentModule,
    StudentTaskResult,
    TaskResult,
)


def is_trainer(user):

    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == "trainer"
    except Profile.DoesNotExist:
        return False


trainer_required = user_passes_test(is_trainer)


@trainer_required
def trainer_home(request):
    students = User.objects.filter(student_group__trainer=request.user).distinct()

    groups = Group.objects.filter(trainer=request.user).order_by("id")

    modules = Module.objects.all().order_by("-created_at")

    return render(
        request,
        "trainer/home.html",
        {
            "students": students,
            "groups": groups,
            "modules": modules,
        },
    )


@trainer_required
def trainer_groups(request):
    students = (
        User.objects.filter(profile__role="student")
        .prefetch_related("student_group__trainer")
        .order_by("username")
    )

    # tylko grupy tego trenera
    groups = Group.objects.filter(trainer=request.user).order_by("name")

    # dopisz “pola” na obiektach studentów (template wtedy używa s.my_group itd.)
    for s in students:
        s.current_group = s.student_group.all().order_by("id").first()  # dowolny trener
        s.my_trainer_group = s.student_group.filter(trainer=request.user).order_by("id").first()
        # zablokuj przypisanie, jeśli student jest w grupie innego trenera
        s.locked_by_other = s.student_group.exclude(trainer=request.user).exists()

    return render(
        request,
        "trainer/groups.html",
        {
            "students": students,
            "groups": groups,
        },
    )


@trainer_required
def trainer_results(request):
    search_query = request.GET.get("search", "")

    students = User.objects.filter(student_group__trainer=request.user).distinct().order_by("username")

    if search_query:
        students = students.filter(username__icontains=search_query)

    return render(
        request,
        "trainer/results.html",
        {"students": students, "search_query": search_query},
    )


@require_POST
@trainer_required
def ajax_create_group(request):
    try:
        data = json.loads(request.body or "{}")
        name = (data.get("name") or "").strip()
        if not name:
            return JsonResponse({"error": "Pusta nazwa grupy"}, status=400)

        group = Group.objects.create(name=name, trainer=request.user)
        return JsonResponse({"id": group.id, "name": group.name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@trainer_required
def ajax_assign_student(request):
    try:
        data = json.loads(request.body or "{}")
        student_id = data.get("student_id")
        group_id = data.get("group_id")  # Can be an ID or null

        if not student_id:
            return JsonResponse({"error": "Brak ID studenta"}, status=400)

        student = get_object_or_404(User, id=student_id)

        # 1. Clear student from any groups owned by THIS trainer
        my_groups = Group.objects.filter(trainer=request.user)
        for g in my_groups:
            g.students.remove(student)

        # 2. If a group_id was provided (and isn't null), add them to that group
        if group_id:
            try:
                group = Group.objects.get(id=group_id, trainer=request.user)
                group.students.add(student)
                return JsonResponse({"status": "ok", "message": "Przypisano do grupy"})
            except (Group.DoesNotExist, ValueError):
                return JsonResponse({"error": "Nieprawidłowa grupa"}, status=400)

        return JsonResponse({"status": "ok", "message": "Usunięto z grupy"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@trainer_required
def trainer_module_add(request):
    module_form = ModuleForm()
    task_form = TaskForm()

    if request.method == "POST":
        # Sprawdzamy, który przycisk został kliknięty
        if "add_task" in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save()
                messages.success(request, f"Dodano nowe zadanie: Task {task.id} ({task.level})")
                return redirect("trainer_module_add")  # Odśwież, by zadanie pojawiło się na liście

        elif "create_module" in request.POST:
            module_form = ModuleForm(request.POST)
            if module_form.is_valid():
                module = module_form.save()
                messages.success(request, f"Utworzono moduł: {module.title}")
                return redirect("trainer_home")

    return render(
        request,
        "trainer/module_add.html",
        {"module_form": module_form, "task_form": task_form},
    )


@trainer_required
def trainer_module_assign(request):
    if request.method != "POST":
        return redirect("trainer_home")

    group_id = request.POST.get("group_id")
    module_id = request.POST.get("module_id")

    group = get_object_or_404(Group, id=group_id, trainer=request.user)
    module = get_object_or_404(Module, id=module_id)

    max_score = module.tasks.count()

    created_count = 0
    for student in group.students.all():
        obj, created = StudentModule.objects.get_or_create(
            student=student,
            module=module,
            defaults={"max_score": max_score},
        )
        # aktualizuj max_score jeśli moduł ma inną liczbę zadań
        if not created and obj.max_score != max_score:
            obj.max_score = max_score
            obj.save(update_fields=["max_score"])

        if created:
            created_count += 1

    datatuple = []
    subject = f"ChessMasters: Nowy moduł zadań - {module.title}"

    students_with_emails = (
        Profile.objects.filter(user__student_group=group, email__isnull=False)
        .exclude(email="")
        .select_related("user")
    )

    for student in students_with_emails:
        recipient_name = student.user.username
        recipient_email = student.user.email
        message = (
            f"Cześć {recipient_name}!\n\n"
            f"Twój trener przypisał Ci nowy moduł z zadaniami: {module.title}.\n\n"
            f"Powodzenia!"
        )

        datatuple.append((subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email]))

    if datatuple:
        send_mass_mail(tuple(datatuple), fail_silently=True)

    messages.success(
        request,
        f"Przypisano moduł '{module.title}' do grupy '{group.name}'. Wysłano {len(datatuple)} powiadomień na email."
        f"Nowe przypisania: {created_count}.",
    )
    return redirect("trainer_home")


@trainer_required
def student_detail_view(request, user_id):
    student = get_object_or_404(User, id=user_id)
    # Pobieramy postępy w modułach dla tego ucznia
    module_progress = StudentModule.objects.filter(student=student).select_related("module")

    return render(
        request,
        "trainer/student_detail.html",
        {"student": student, "module_progress": module_progress},
    )


@trainer_required
def student_module_detail_view(request, user_id, module_id):
    student = get_object_or_404(User, id=user_id)
    module = get_object_or_404(Module, id=module_id)
    student_module = get_object_or_404(StudentModule, student=student, module=module)
    # Wyniki każdego osobnego zadania
    task_results = (
        StudentTaskResult.objects.filter(student=student, module=module)
        .select_related("task")
        .order_by("timestamp")
    )

    total_tasks_in_module = module.tasks.count()
    tasks_attempted = task_results.count()
    correct_tasks = task_results.filter(is_correct=True).count()

    accuracy = (correct_tasks / tasks_attempted * 100) if tasks_attempted > 0 else 0

    context = {
        "student": student,
        "module": module,
        "student_module": student_module,
        "task_results": task_results,
        "total_tasks": total_tasks_in_module,
        "tasks_attempted": tasks_attempted,
        "accuracy": round(accuracy, 1),
    }

    return render(request, "trainer/student_module_detail.html", context)
