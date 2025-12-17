from django.urls import path

from .views import ajax, auth, student, trainer

urlpatterns = [
    # Auth
    path("", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("register/", auth.register_view, name="register"),
    # Student
    # TODO: some of the post requests are asynchronous and some are not, refactor to a single format at some time
    path("student/", student.student_dashboard, name="student_dashboard"),
    path("save-result/", student.save_result, name="save_result"),
    path("results/", student.results_view, name="results"),
    # Trainer
    path("trainer/", trainer.trainer_home, name="trainer_home"),
    path("trainer/groups/", trainer.trainer_groups, name="trainer_groups"),
    path("trainer/results", trainer.trainer_results, name="trainer_results"),
    # Trainer (json endpoints)
    path("trainer/ajax/group/create/", ajax.create_group, name="ajax_create_group"),
    path(
        "trainer/ajax/group/assign/",
        ajax.assign_student,
        name="ajax_assign_student",
    ),
]
