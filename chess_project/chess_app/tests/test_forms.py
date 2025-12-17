from chess_app.forms import RegisterForm
from chess_app.models import Profile
from django.test import TestCase


class PasswordTest(TestCase):

    def test_password_cannot_be_empty(self):
        form = RegisterForm(
            data={
                "username": "testuser",
                "password1": "",
                "password2": "",
                "role": Profile.ROLE_CHOICES[0][0],
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_password_too_short_is_rejected(self):
        form = RegisterForm(
            data={
                "username": "testuser",
                "password1": "ab",
                "password2": "ab",
                "role": Profile.ROLE_CHOICES[0][0],
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_password_with_3_characters_is_accepted(self):
        form = RegisterForm(
            data={
                "username": "testuser",
                "password1": "abc",
                "password2": "abc",
                "role": Profile.ROLE_CHOICES[0][0],
            }
        )
        self.assertTrue(form.is_valid())
