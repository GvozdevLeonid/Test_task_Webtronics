"""
Test recipe API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Recipe,
    Tag,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
)


RECIPE_URL = reverse('recipe:recipe-list')


def detail_recipe_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_tag(user, name='tag'):
    return Tag.objects.create(user=user, name=name)


def create_recipe(user, **kw):
    default_values = {
        'title': 'Default title',
        'time_minutes': 1,
        'price': 0,
        'description': 'Default description',
        'link': 'https://some_website.com',
    }
    default_values.update(kw)

    return Recipe.objects.create(user=user, **default_values)


class PublicRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test if authenticate is required for RECIPE_URL."""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_recipe(self):
        """Test authenticate required for create recipe."""

        payload = {
            'title': 'title',
            'description': 'description',
            'time_minutes': 0,
            'price': 0.0,
            'link': 'https://some_website.com'
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    def setUp(self):
        user_data = {
            'name': 'test',
            'email': 'test@example.com',
            'password': 'password',
        }

        self.user = get_user_model().objects.create_user(**user_data)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes."""

        create_recipe(self.user)
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_limited_recipes(self):
        """Test retrieving limit list of recipes for user."""
        second_user = get_user_model().objects.create_user(
                name='name',
                email='test2@example.com',
                password='password',
        )

        create_recipe(self.user)
        create_recipe(self.user)

        create_recipe(second_user)
        create_recipe(second_user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(self.user)
        detail_url = detail_recipe_url(recipe.id)

        res = self.client.get(detail_url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test recipe is created successful."""

        payload = {
            'title': 'title',
            'description': 'description',
            'time_minutes': 5,
            'price': 5.0,
            'link': 'https://some_website.com'
        }

        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test for partial update recipe."""
        payload = {
            'title': 'New title',
            'description': 'New description',
        }

        recipe = create_recipe(self.user)
        res = self.client.patch(detail_recipe_url(recipe.id), payload)
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, res.data['title'])
        self.assertEqual(recipe.description, res.data['description'])

    def test_full_update_recipe(self):
        """Test for full update recipe."""

        payload = {
            'title': 'New title',
            'time_minutes': 999,
            'price': 999,
            'link': 'https://some_new_link.com',
            'description': 'New description',
        }

        recipe = create_recipe(self.user)
        res = self.client.put(detail_recipe_url(recipe.id), payload)
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_return_error(self):
        """Test that cant update user."""
        second_user = get_user_model().objects.create_user(
                name='name',
                email='test2@example.com',
                password='password',
        )

        recipe = create_recipe(self.user)

        res = self.client.patch(detail_recipe_url(recipe.id),
                                {'user': second_user.id},
                                )
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe is successful"""
        recipe = create_recipe(self.user)

        res = self.client.delete(detail_recipe_url(recipe.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_another_user_recipe(self):
        """Test deleting another user recipe rise error."""
        second_user = get_user_model().objects.create_user(
                name='name',
                email='test2@example.com',
                password='password',
        )

        recipe = create_recipe(second_user)

        res = self.client.delete(detail_recipe_url(recipe.id))

        self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_add_tags_to_recipe(self):
        """Test add some tags."""

        recipe = create_recipe(self.user)
        tag1 = create_tag(user=self.user, name='WWW')
        tag2 = create_tag(user=self.user, name='AAA')

        tags = Tag.objects.all().order_by("id")
        serializer = TagSerializer(tags, many=True)

        payload = {
            'tags': [
                {'name': tag1.name},
                {'name': tag2.name},
            ]
        }

        res = self.client.patch(detail_recipe_url(recipe.id),
                                payload,
                                format='json',
                                )

        recipe.refresh_from_db()

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['tags'], serializer.data)

    def test_add_and_create_tags_to_recipe(self):
        """Test add and create some tags."""

        recipe = create_recipe(self.user)
        tag1 = create_tag(user=self.user, name='WWW')
        tag2 = create_tag(user=self.user, name='AAA')

        tags = Tag.objects.all().order_by("id")
        serializer = TagSerializer(tags, many=True)

        payload = {
            'tags': [
                {'name': tag1.name},
                {'name': tag2.name},
                {'name': 'KKK'},
            ]
        }

        res = self.client.patch(detail_recipe_url(recipe.id),
                                payload,
                                format='json',
                                )

        recipe.refresh_from_db()

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['tags'], serializer.data)
