from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg

class Profile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("trainer", "Trainer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class TaskResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=20)  # easy / medium / hard
    score = models.IntegerField()  # 0–5 correct answers
    avg_time = models.FloatField()  # seconds
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} – {self.level} – {self.score}/5"
    
    @classmethod
    def average_time_for_user(cls, user):
        return cls.objects.filter(user=user).aggregate(
            Avg("avg_time")
        )["avg_time__avg"]

class Task(models.Model):
    fen = models.CharField(max_length=100)
    correct_move = models.CharField(max_length=10)
    level = models.CharField(max_length=20, default="easy")
    def __str__(self):
        return f"Task {self.id} ({self.level})"