"""
Admin models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class AdminUser(BaseUserAdmin):
    ordering = ['id']
    list_display = ["email", "name"]
    search_fields = ["name", "email"]
    list_filter = ["is_superuser"]
    readonly_fields = ["last_login"]
    fieldsets = (
        (_("User"), {"fields": ("name", "email", "password")}),
        (_("Permissions"), {"fields": (
                                "is_active",
                                "is_staff",
                                "is_superuser",
                                "groups",
                                )
                            }),
        (_("Last visited"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "name",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                ),
        }),
    )


admin.site.register(models.User, AdminUser)
