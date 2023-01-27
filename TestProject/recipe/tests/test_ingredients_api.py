"""
Tests tags API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Recipe,
    Ingredient,
)
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse("recipe:ingredient-list")


def detail_ingredient_url(ingredient_id):
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


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


def create_user(**kw):
    default_values = {
        'name': 'name',
        'email': 'email@example.com',
        'password': 'password',
    }
    default_values.update(kw)

    return get_user_model().objects.create_user(**default_values)


def create_ingredient(user, name='ingredient', quantity=0.5):
    return Ingredient.objects.create(user=user, name=name, quantity=quantity)


class PublicIngredientApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_ingredients(self):
        """Test if authenticate is required for INGREDIENT_URL."""

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_ingredient(self):
        """Test authenticate required for create ingredient."""

        payload = {
            'name': 'ingredient',
            'quantity': 2.5,
            'user': create_user(),
        }

        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving list of ingredients."""
        create_ingredient(self.user, 'ingredient1')
        create_ingredient(self.user, 'ingredient2')
        create_ingredient(self.user, 'ingredient3')

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_ingredient(self):
        """Test create ingredient is successful."""
        payload = {
            'name': 'ingredient1',
            'quantity': 2.5,
            'user': self.user,
        }
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ingredient.objects.filter(id=res.data['id']).exists())

    def test_retrieve_limited_ingredients(self):
        """Test retrieve list of ingredients for user."""
        second_user = create_user(email='second_user@example.com')
        create_ingredient(second_user)
        create_ingredient(second_user)
        create_ingredient(self.user)
        create_ingredient(self.user)

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.filter(
                user=self.user
        ).order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_tag(self):
        """Test update ingredient."""
        ingredient = create_ingredient(self.user)
        res = self.client.patch(detail_ingredient_url(ingredient.id),
                                {'name': "New ingredient Name"},
                                )
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], ingredient.name)

    def test_delete_ingredient(self):
        """Test delete ingredient by user."""
        ingredient = create_ingredient(self.user)
        res = self.client.delete(detail_ingredient_url(ingredient.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_delete_another_user_tag(self):
        """Test deleting another user ingredient rise error."""
        another_user = create_user(email='anotheruser@example.com')
        ingredient = create_ingredient(another_user)
        res = self.client.delete(detail_ingredient_url(ingredient.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_update_tag_return_error(self):
        """Test that cant update ingredient by another user."""
        another_user = create_user(email='anotheruser@example.com')
        ingredient = create_ingredient(user=another_user,
                                       name='Ingredient Name',
                                       )

        res = self.client.patch(detail_ingredient_url(ingredient.id),
                                {'name': 'New Ingredient Name'},
                                )
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ingredient.name, 'Ingredient Name')

    def test_update_user_return_error(self):
        """Test that cant update user in ingredient rise error."""
        another_user = create_user(email='anotheruser@example.com')
        ingredient = create_ingredient(user=self.user)

        res = self.client.patch(detail_ingredient_url(ingredient.id),
                                {'user': another_user.id},
                                )
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.user, self.user)

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes."""

        ingredient1 = create_ingredient(self.user, name='ingredient1')
        ingredient2 = create_ingredient(self.user, name='ingredient2')

        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient1)

        params = {'assigned_only': 1}
        res = self.client.get(INGREDIENT_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        si1 = IngredientSerializer(ingredient1)
        si2 = IngredientSerializer(ingredient2)
        self.assertIn(si1.data, res.data)
        self.assertNotIn(si2.data, res.data)
