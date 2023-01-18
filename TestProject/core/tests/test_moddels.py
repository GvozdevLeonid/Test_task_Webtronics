"""
Test Models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_user_model_create(self):
        """Create New user."""
        user_email = "TestEmail@example.com"
        user_password = "Password"

        new_user = get_user_model().objects.create_user(
                email=user_email,
                password=user_password,
        )

        self.assertEqual(new_user.email, user_email)
        self.assertTrue(new_user.check_password(user_password))

    def test_user_email_normalized(self):
        """If user email is normalized."""
        emails = [
            ["USER1@example.COM", "USER1@example.com"],
            ["user2@EXAMPLE.com", "user2@example.com"],
            ["User3@EXAMPLE.COM", "User3@example.com"],
            ["UseR4@Example.com", "UseR4@example.com"],
            ["  UseR5@example.com", "UseR5@example.com"],
            ["UseR6@example.com  ", "UseR6@example.com"],
            ["UseR7 @example.com", "UseR7@example.com"],
            ["UseR8@ example.com", "UseR8@example.com"],
            [" UseR9@ EXAMPLE. CoM  ", "UseR9@example.com"],
        ]

        for email, expected_result in emails:
            user = get_user_model().objects.create_user(email, "password")

            self.assertEqual(user.email, expected_result)

    def test_empty_user_email(self):
        """If user have not email raised ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', "password")
            get_user_model().objects.create_user("@example.com", "password")

    def test_create_superuser(self):
        """Create superuser."""

        user = get_user_model().objects.create_superuser(
                "Superuser@example.com",
                "password",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
