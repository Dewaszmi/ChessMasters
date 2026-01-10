import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..models import Group


@require_POST
def create_group(request):
    """Tworzy nową grupę przypisaną do zalogowanego trenera."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=403)

    # Weryfikacja roli trenera
    if (
        getattr(request.user, "profile", None) is None
        or request.user.profile.role != "trainer"
    ):
        return JsonResponse({"error": "forbidden"}, status=403)

    try:
        data = json.loads(request.body or "{}")
        name = (data.get("name") or "").strip()

        if not name:
            return JsonResponse({"error": "empty name"}, status=400)

        group = Group.objects.create(name=name, trainer=request.user)
        return JsonResponse({"id": group.id, "name": group.name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def assign_student(request):
    """Przypisuje studenta do konkretnej grupy trenera."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=403)

    if (
        getattr(request.user, "profile", None) is None
        or request.user.profile.role != "trainer"
    ):
        return JsonResponse({"error": "forbidden"}, status=403)

    try:
        data = json.loads(request.body or "{}")
        student_id = data.get("student_id")
        group_id = data.get("group_id")

        if not student_id or not group_id:
            return JsonResponse({"error": "missing params"}, status=400)

        student = User.objects.get(id=student_id)

        # Trener może przypisać tylko do swojej grupy
        group = Group.objects.get(id=group_id, trainer=request.user)

        # Usuwamy studenta z innych grup TEGO SAMEGO trenera
        for g in Group.objects.filter(trainer=request.user, students=student).exclude(
            id=group.id
        ):
            g.students.remove(student)

        group.students.add(student)

        return JsonResponse({"status": "ok", "group_name": group.name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

