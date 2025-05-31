import pytest
from django.contrib.auth import get_user_model

from .factories import AttendeeFactory, OrganizerFactory

User = get_user_model()


@pytest.mark.django_db
def test_organizer_user_creation():
    """
    Test that a user created via OrganizerFactory has the 'organizer' role.
    """
    organizer = OrganizerFactory()

    assert organizer.id is not None
    assert organizer.username.startswith("user")
    assert organizer.email.startswith("user")
    assert organizer.role == "organizer"
    assert organizer.check_password("password123")


@pytest.mark.django_db
def test_user_str_representation():
    """
    Test the __str__ method of the User model.
    """
    user = AttendeeFactory(username="samadams")
    assert str(user) == "samadams"
