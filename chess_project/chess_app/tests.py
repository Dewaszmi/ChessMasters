from django.test import TestCase

from django.test import TestCase
from chess_app.forms import RegisterForm
from django.contrib.auth.models import User
from chess_app.models import TaskResult
from chess_app.models import Profile

class PasswordTest(TestCase):

    def test_password_cannot_be_empty(self):
        form = RegisterForm(data={
            'username': 'testuser',
            'password1': '',
            'password2': '',
            'role': Profile.ROLE_CHOICES[0][0],
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_password_too_short_is_rejected(self):
        form = RegisterForm(data={
            'username': 'testuser',
            'password1': 'ab',
            'password2': 'ab',
            'role': Profile.ROLE_CHOICES[0][0],
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_password_with_3_characters_is_accepted(self):
        form = RegisterForm(data={
            'username': 'testuser',
            'password1': 'abc',
            'password2': 'abc',
            'role': Profile.ROLE_CHOICES[0][0],
        })
        self.assertTrue(form.is_valid())


class TaskResultAvgTimeTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="secret"
        )

    def test_average_time_across_all_levels(self):
        TaskResult.objects.create(
            user=self.user,
            level="easy",
            score=4,
            avg_time=2.0
        )
        TaskResult.objects.create(
            user=self.user,
            level="medium",
            score=5,
            avg_time=4.0
        )
        TaskResult.objects.create(
            user=self.user,
            level="hard",
            score=3,
            avg_time=6.0
        )

        avg = TaskResult.average_time_for_user(self.user)

        self.assertEqual(avg, 4.0)
