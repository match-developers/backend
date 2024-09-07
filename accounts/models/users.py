from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomAccountManager

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(_("User Name"), max_length=150)
    first_name = models.CharField(_("First Name"), max_length=150)
    last_name = models.CharField(_("last Name"), max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False
    )

    objects = CustomAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name"]

    def __str__(self):
        return self.email