from django.contrib import admin
from .models import Profile, Task, TaskResult, Group, Module, StudentModule

# Rejestrujemy każdy model dokładnie raz
admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(TaskResult)
admin.site.register(Group)
admin.site.register(Module)
admin.site.register(StudentModule)