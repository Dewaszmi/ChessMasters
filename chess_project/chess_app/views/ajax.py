import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..models import Group


@csrf_exempt
@require_POST
def create_group(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=403)

    data = json.loads(request.body)
    name = data.get("name")

    if not name:
        return JsonResponse({"error": "empty name"}, status=400)

    group = Group.objects.create(name=name, trainer=request.user)
    return JsonResponse({"id": group.id, "name": group.name})


@csrf_exempt
@require_POST
def assign_student(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=403)

    data = json.loads(request.body)
    student_id = data.get("student_id")
    group_id = data.get("group_id")

    student = User.objects.get(id=student_id)
    group = Group.objects.get(id=group_id, trainer=request.user)

    for g in Group.objects.filter(students=student):
        g.students.remove(student)

    group.students.add(student)

    return JsonResponse({"status": "ok"})
