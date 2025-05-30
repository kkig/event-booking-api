import factory
from common.choices import UserRole
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
    role = UserRole.ATTENDEE

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        # Manually save after postgeneration
        if create:
            obj.save()


class OrganizerFactory(UserFactory):
    role = UserRole.ORGANIZER
