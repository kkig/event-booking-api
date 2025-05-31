import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_organizer_user_creation(organizer_factory):
    """
    Test that a user created via OrganizerFactory has the 'organizer' role.
    """
    organizer = organizer_factory.create()

    assert organizer.id is not None
    assert organizer.username.startswith("user")
    assert organizer.email.startswith("user")
    assert organizer.role == "organizer"
    assert organizer.check_password("password123")


@pytest.mark.django_db
def test_user_str_representation(attendee_factory):
    """
    Test the __str__ method of the User model.
    """
    user = attendee_factory.create(username="samadams")
    assert str(user) == "samadams"
