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
    Tag,
)
from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


def detail_tag_url(tag_id):
    return reverse("recipe:tag-detail", args=[tag_id])


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


def create_tag(user, name='tag'):
    return Tag.objects.create(user=user, name=name)


class PublicTagApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_tags(self):
        """Test if authenticate is required for TAGS_URL."""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tag(self):
        """Test authenticate required for create tag."""

        payload = {
            'name': 'tag1',
            'user': create_user()
        }

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving list of tags."""
        create_tag(self.user, 'tag1')
        create_tag(self.user, 'tag2')
        create_tag(self.user, 'tag3')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag(self):
        """Test create tag is successful."""
        payload = {
            'name': 'Tag1',
            'user': self.user,
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(id=res.data['id']).exists())

    def test_retrieve_limited_tag(self):
        """Test retrieve list of tags for user."""
        second_user = create_user(email='second_user@example.com')
        create_tag(second_user)
        create_tag(second_user)
        create_tag(self.user)
        create_tag(self.user)

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.filter(user=self.user).order_by('name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_tag(self):
        """Test update tag."""
        tag = create_tag(self.user)
        res = self.client.patch(detail_tag_url(tag.id),
                                {'name': "New Tag Name"},
                                )
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], tag.name)

    def test_delete_tag(self):
        """Test delete tag by user."""
        tag = create_tag(self.user)
        res = self.client.delete(detail_tag_url(tag.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_delete_another_user_tag(self):
        """Test deleting another user tag rise error."""
        another_user = create_user(email='anotheruser@example.com')
        tag = create_tag(another_user)
        res = self.client.delete(detail_tag_url(tag.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_update_tag_return_error(self):
        """Test that cant update tag by another user."""
        another_user = create_user(email='anotheruser@example.com')
        tag = create_tag(user=another_user, name='Tag Name')

        res = self.client.patch(detail_tag_url(tag.id),
                                {'name': 'New Tag Name'},
                                )
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(tag.name, 'Tag Name')

    def test_update_user_return_error(self):
        """Test that cant update user in tag rise error."""
        another_user = create_user(email='anotheruser@example.com')
        tag = create_tag(user=self.user, name='Tag Name')

        res = self.client.patch(detail_tag_url(tag.id),
                                {'user': another_user.id},
                                )
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.user, self.user)
