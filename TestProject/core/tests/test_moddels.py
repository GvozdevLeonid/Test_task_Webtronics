"""
Test Models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch

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

    def test_create_recipe(self):
        """Test create a new recipe."""
        user_data = {
            'email': 'test@example.com',
            'name': 'test',
            'password': 'password',
        }

        user = get_user_model().objects.create_user(**user_data)

        recipe = models.Recipe.objects.create(
                user=user,
                title='Title',
                time_minutes=5,
                price=5.5,
                description="description",
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test create new tag successful."""

        user = get_user_model().objects.create_user(
                "user@example.com",
                "password",
        )

        tag = models.Tag.objects.create(user=user, name='Tag')

        self.assertEqual(tag.name, str(tag))

    def test_create_ingredient(self):
        """Test create new ingredient successful."""
        user = get_user_model().objects.create_user(
                "user@example.com",
                "password",
        )

        ingredient = models.Ingredient.objects.create(user=user,
                                                      name='ingredient',
                                                      quantity=2.5)

        self.assertEqual(ingredient.name, str(ingredient))

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generate image path."""
        uuid = 'Test-UUID'
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')