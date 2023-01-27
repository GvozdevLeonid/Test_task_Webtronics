"""
Database Models.
"""
import uuid
import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def recipe_image_file_path(instance, file_name):
    file_extension = os.path.splitext(file_name)[1]
    file_name = f'{uuid.uuid4()}{file_extension}'
    return os.path.join('uploads', 'recipe', file_name)


class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, password=None, **kw):
        """Create, save and return new user."""
        if not email or not email.split("@")[0]:
            raise ValueError("User must have email.")
        user = self.model(email=self.normalize_email(email), **kw)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password=None, **kw):
        """Create and return new Superuser."""
        return self.create_user(email,
                                password,
                                is_staff=True,
                                is_superuser=True,
                                **kw
                                )

    def normalize_email(self, email):
        name, domain = email.split("@")
        return f"{name.replace(' ', '')}@{domain.replace(' ','').lower()}"


class User(AbstractBaseUser, PermissionsMixin):
    """User."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe object."""
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,
                                decimal_places=2,
                                )
    description = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             )
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')

    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag object."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient object."""

    name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=5,
                                   decimal_places=2,
                                   )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             )

    def __str__(self):
        return self.name
