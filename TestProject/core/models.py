"""
Database Models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


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
