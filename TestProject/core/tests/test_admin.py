"""
Test Django admin.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdmitTests(TestCase):
    """Test django admin."""

    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
                email="admin@example.com",
                password="password",
                name="admin",
        )
        self.user = get_user_model().objects.create_user(
                email="user@example.com",
                password="password",
                name="user",
        )

        self.client = Client()
        self.client.force_login(self.admin)

    def test_users_list(self):
        url = reverse("admin:core_user_changelist")

        result = self.client.get(url)

        self.assertContains(result, self.user.email)
        self.assertContains(result, self.user.name)
