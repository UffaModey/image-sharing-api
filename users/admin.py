from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from . import models


@admin.register(models.User)
class UserAdmin(AuthUserAdmin):
    model = models.User
    list_display = (
        "username",
        "is_staff",
        "email",
        "first_name",
        "last_name",
        "is_active",
    )
