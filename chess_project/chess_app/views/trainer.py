import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import ModuleForm
from ..models import Group, Module, Profile, TaskResult
from chess_app.models import StudentModule



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
  
    students = User.objects.filter(profile__role="student")

 
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
        User.objects
        .filter(profile__role="student")
        .prefetch_related("student_group__trainer")
        .order_by("username")
    )

    # tylko grupy tego trenera
    groups = Group.objects.filter(trainer=request.user).order_by("name")

    # dopisz “pola” na obiektach studentów (template wtedy używa s.my_group itd.)
    for s in students:
        s.current_group = s.student_group.all().order_by("id").first()  # dowolny trener
        s.my_group = s.student_group.filter(trainer=request.user).order_by("id").first()
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
    results = TaskResult.objects.select_related("user").order_by("-created_at")
    return render(request, "trainer/results.html", {"results": results})




@require_POST
@trainer_required
def ajax_create_group(request):
    data = json.loads(request.body or "{}")
    name = (data.get("name") or "").strip()

    if not name:
        return JsonResponse({"error": "empty name"}, status=400)

    group = Group.objects.create(name=name, trainer=request.user)
    return JsonResponse({"id": group.id, "name": group.name})


@require_POST
@trainer_required
def ajax_assign_student(request):
    data = json.loads(request.body or "{}")
    student_id = data.get("student_id")
    group_id = data.get("group_id")

    if not student_id or not group_id:
        return JsonResponse({"error": "missing student_id/group_id"}, status=400)

    student = get_object_or_404(User, id=student_id)
    group = get_object_or_404(Group, id=group_id, trainer=request.user)


    for g in Group.objects.filter(students=student):
        g.students.remove(student)

    group.students.add(student)

    return JsonResponse({"status": "ok"})


@trainer_required
def trainer_module_add(request):
    if request.method == "POST":
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.save()
            form.save_m2m()
            messages.success(request, f"Utworzono moduł: {module.title}")
            return redirect("trainer_home")
    else:
        form = ModuleForm()

    return render(request, "trainer/module_add.html", {"form": form})


@login_required
def trainer_module_assign(request):
    # dodatkowy bezpiecznik
    if not is_trainer(request.user):
        return HttpResponseForbidden("Brak dostępu")

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

    messages.success(
        request,
        f"Przypisano moduł '{module.title}' do grupy '{group.name}'. "
        f"Nowe przypisania: {created_count}."
    )
    return redirect("trainer_home")
