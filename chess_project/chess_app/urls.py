from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("trainer/", views.trainer_dashboard, name="trainer_dashboard"),
]
