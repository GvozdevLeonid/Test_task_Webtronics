"""
Test user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**kw):
    return get_user_model().objects.create_user(**kw)


class PublicUserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create a user is successful."""
        payload = {
            "email": "TestExample@example.com",
            "password": "password",
            "name": "name",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn(payload['password'], res.data)

    def test_create_user_with_email_exist_error(self):
        """Test create new user with email exist."""
        payload = {
            "email": "TestExample@example.com",
            "password": "password",
            "name": "name",
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_short_password(self):
        """Test return error when password less than 5 char."""
        payload = {
            "email": "TestExample@example.com",
            "password": "pwd",
            "name": "name",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user)

    def test_create_token_for_user(self):
        """Test create and return token for auth user."""
        payload = {
            "email": "TestExample@example.com",
            "password": "password",
            "name": "name",
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_with_blank_email(self):
        """Test return error when email is empty."""
        payload = {
            "email": "TestExample@example.com",
            "password": "password",
            "name": "name",
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, {'email': '',
                                           'password': 'password',
                                           })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_with_blank_password(self):
        """Test return error when password is empty."""
        payload = {
            "email": "TestExample@example.com",
            "password": "password",
            "name": "name",
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, {'email': 'TestExample@example.com',
                                           'password': '',
                                           })

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_with_non_existent_user(self):
        """Test return error when non existent user."""
        payload = {
            "email": "TestExample@example.com",
            "password": "password",
            "name": "name",
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_authenticate_is_required(self):
        """Test if authenticate is required for ME_URL."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    def setUp(self):
        payload = {
            "email": "TestExample@example.com",
            "password": "password",
            "name": "name",
        }

        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieve profile for logged inn user."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
                res.data,
                {
                    "name": "name",
                    "email": "TestExample@example.com",
                }
        )

    def test_post_method_not_allowed(self):
        """Test retrieve profile for logged inn user."""

        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test if user can update name, email and password."""
        payload = {
            "name": "New name",
            "password": "New password"
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
