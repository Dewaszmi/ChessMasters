from django.urls import path

from .views import ajax, auth, student, trainer

urlpatterns = [
  
    path("", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("register/", auth.register_view, name="register"),

   
    path("student/", student.student_dashboard, name="student_dashboard"),
    path("save-result/", student.save_result, name="save_result"),
    path("results/", student.results_view, name="results"),
    path('get-module-tasks/<int:module_id>/', student.get_module_tasks, name='get_module_tasks'),

  
    path("trainer/", trainer.trainer_home, name="trainer_home"),
    path("trainer/groups/", trainer.trainer_groups, name="trainer_groups"),
    path("trainer/results/", trainer.trainer_results, name="trainer_results"),
    path("trainer/modules/add/", trainer.trainer_module_add, name="trainer_module_add"),
    path("trainer/modules/assign/", trainer.trainer_module_assign, name="trainer_module_assign"),

   
    path('ajax/create-group/', ajax.create_group, name='ajax_create_group'),
    path('ajax/assign-student/', ajax.assign_student, name='ajax_assign_student'),

]
