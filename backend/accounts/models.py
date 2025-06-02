from common.choices import UserRole
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(max_length=10, choices=UserRole)

    def __str__(self):
        return self.username
