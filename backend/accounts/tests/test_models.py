import pytest
from common.choices import UserRole
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_attendee_user_creation(attendee_factory):
    """
    Test that a user created via AttendeeFactory has the 'attendee' role.
    """
    attendee = attendee_factory.create()

    assert attendee.id is not None
    assert attendee.username.startswith("user")
    assert attendee.email.startswith("user")
    assert attendee.role == UserRole.ATTENDEE
    assert attendee.check_password("password123")


@pytest.mark.django_db
def test_organizer_user_creation(organizer_factory):
    """
    Test that a user created via OrganizerFactory has the 'organizer' role.
    """
    organizer = organizer_factory.create()

    assert organizer.id is not None
    assert organizer.username.startswith("user")
    assert organizer.email.startswith("user")
    assert organizer.role == UserRole.ORGANIZER
    assert organizer.check_password("password123")


@pytest.mark.django_db
def test_user_str_representation(attendee_factory):
    """
    Test the __str__ method of the User model.
    """
    user = attendee_factory.create(username="samadams")
    assert str(user) == "samadams"


@pytest.mark.django_db
def test_user_role_choices(user_factory):
    """
    Test that user roles can be set to valid choices.
    """
    organizer_user = user_factory.create(role=UserRole.ORGANIZER)
    assert organizer_user.role == UserRole.ORGANIZER

    attendee_user = user_factory.create(role=UserRole.ATTENDEE)
    assert attendee_user.role == UserRole.ATTENDEE
