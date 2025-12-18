import json

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.contrib.auth.models import User
from ..models import Module, Group

from ..models import Group, TaskResult


# helper decorator to check if user is authenticated and a trainer
def is_trainer(user):
    return user.is_authenticated and user.profile.role == "trainer"


trainer_required = user_passes_test(is_trainer)




def trainer_home(request):
    students = User.objects.filter(profile__role='student')
    groups = Group.objects.all()
    modules = Module.objects.all()

    return render(request, "trainer/home.html", {
        "students": students,
        "groups": groups,
        "modules": modules
    })


@trainer_required
def trainer_groups(request):
    students = User.objects.filter(profile__role="student")
    groups = Group.objects.filter(trainer=request.user)

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
    return render(
        request,
        "trainer/results.html",
        {"results": results},
    )


@require_POST
def ajax_create_group(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is unauthorized"}, status=403)

    data = json.loads(request.body)
    name = data.get("name")

    if not name:
        return JsonResponse({"error": "empty name"}, status=400)

    group = Group.objects.create(name=name, trainer=request.user)

    return JsonResponse({"id": group.id, "name": group.name})


@require_POST
def ajax_assign_student(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is unauthorized"}, status=403)

    data = json.loads(request.body)
    student_id = data.get("student_id")
    group_id = data.get("group_id")

    student = User.objects.get(id=student_id)
    group = Group.objects.get(id=group_id, trainer=request.user)

    for g in Group.objects.filter(students=student):
        g.students.remove(student)

    group.students.add(student)

    return JsonResponse({"status": "ok"})
