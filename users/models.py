from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models

from isa.models import TimeStampedUUIDModel

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self,
        username: str,
        password: str,
        is_staff: bool,
        is_superuser: bool,
        **extra_fields,
    ):
        user = self.model(
            username=username,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username: str, password=None, **extra_fields):
        return self._create_user(username, password, False, False, **extra_fields)

    def create_superuser(self, username: str, password: str, **extra_fields):
        return self._create_user(username, password, True, True, **extra_fields)

class User(AbstractBaseUser, TimeStampedUUIDModel, PermissionsMixin):
    first_name = models.CharField(_("First Name"), max_length=120, null=True, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=120, null=True, blank=True)
    email = models.EmailField(_("Email Address"), null=True, blank=True)
    username = models.CharField("Username", unique=True, max_length=225)
    is_staff = models.BooleanField(_("staff status"),default=False)
    is_active = models.BooleanField("active",default=True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = "username"
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                name="unique_email_when_not_null_or_empty",
                condition=~models.Q(email__isnull=True) & ~models.Q(email=""),
            )
        ]

    def __str__(self):
        return str(self.username)
