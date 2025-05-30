import factory
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

        # Reuse existing one if available
        django_get_or_create = ("email",)

    # Generates a unique value for each instance
    username = factory.Sequence(lambda n: f"user{n}")

    # Automatically derived from username
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

    # Hashed via set_password() - required to pass user.check_password()
    password = factory.PostGenerationMethodCall(
        "set_password", "password123"  # Default password for tests
    )
    role = "attendee"


class OrganizerFactory(UserFactory):
    role = "organizer"
