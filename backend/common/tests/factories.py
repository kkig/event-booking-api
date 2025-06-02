import factory
from common.choices import UserRole
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

        # Prevent creating duplicate users if username exists
        django_get_or_create = ("username",)
        skip_postgeneration_save = True

    # Generates a unique value for each instance
    username = factory.Sequence(lambda n: f"user{n}")

    # Automatically derived from username
    email = factory.Sequence(lambda n: f"user{n}@example.com")

    # Hashed via set_password() - required to pass user.check_password()
    password = factory.PostGenerationMethodCall(
        "set_password", "password123"  # Default password for tests
    )
    role = UserRole.ATTENDEE


class OrganizerFactory(UserFactory):
    role = UserRole.ORGANIZER


class AttendeeFactory(UserFactory):
    role = UserRole.ATTENDEE
