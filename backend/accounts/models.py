from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOISES = (
        # (value_in_db, human_readable_label)
        ("attendee", "Attendee"),
        ("organizer", "Organizer"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOISES)
