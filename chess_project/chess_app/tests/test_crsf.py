import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from chess_app.models import Profile


class CSRFProtectionTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_csrf_blocked_without_token(self):
        """
        POST to a CSRF-protected view (register) without CSRF token
        should return 403 Forbidden.
        """
        response = self.client.post(
            reverse("register"),
            data={
                "username": "testuser",
                "password1": "pass12345",
                "password2": "pass12345",
                "role": Profile.ROLE_CHOICES[0][0],
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_csrf_allows_with_token(self):
        """
        POST to the same view with a valid CSRF token should succeed.
        """
        # First, get the CSRF token
        response = self.client.get(reverse("register"))
        csrf_token = response.cookies["csrftoken"].value

        response = self.client.post(
            reverse("register"),
            data={
                "username": "testuser",
                "password1": "pass12345",
                "password2": "pass12345",
                "role": Profile.ROLE_CHOICES[0][0],
            },
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        # Should succeed (redirect to login)
        self.assertEqual(response.status_code, 302)
