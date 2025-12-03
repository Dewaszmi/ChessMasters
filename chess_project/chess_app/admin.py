from django.contrib import admin

from .models import TaskResult

# Register your models here.


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ("user", "level", "score", "avg_time", "created_at")
    list_filter = ("level", "user")
    search_fields = ("user__username",)
