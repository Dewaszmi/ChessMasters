from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("trainer/", views.trainer_dashboard, name="trainer_dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register_view, name="register"),
    path("save-result/", views.save_result, name="save_result"),
    path("save-result/", views.save_result, name="save_result"),
    path("results/", views.results_view, name="results"),
]
