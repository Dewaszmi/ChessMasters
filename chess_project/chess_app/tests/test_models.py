from chess_app.models import TaskResult
from django.contrib.auth.models import User
from django.test import TestCase


class TaskResultAvgTimeTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="secret")

    def test_average_time_across_all_levels(self):
        TaskResult.objects.create(user=self.user, level="easy", score=4, avg_time=2.0)
        TaskResult.objects.create(user=self.user, level="medium", score=5, avg_time=4.0)
        TaskResult.objects.create(user=self.user, level="hard", score=3, avg_time=6.0)

        avg = TaskResult.average_time_for_user(self.user)

        self.assertEqual(avg, 4.0)
