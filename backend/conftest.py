import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from apps.accounts.tests.factories import AttendeeFactory, OrganizerFactory, UserFactory

# Import factories
from apps.bookings.tests.factories import BookingFactory, BookingItemFactory
from apps.events.tests.factories import EventFactory, TicketTypeFactory

# === Register the factories as fixtures ===
# By default, the fixture name will be the lowercase class name

# Accounts
register(UserFactory)
register(OrganizerFactory)
register(AttendeeFactory)

# Events
register(EventFactory)
register(TicketTypeFactory)

# bookings
register(BookingFactory)
register(BookingItemFactory)


# === Define Common API Client Fixtures ===


@pytest.fixture
def api_client():
    """
    Base DRF APIClient without authentication.
    """
    return APIClient()


@pytest.fixture
def api_client_factory():
    def _create():
        return APIClient()

    return _create


@pytest.fixture
def attendee_client(attendee_factory, api_client):
    """
    Return an API client authenticated as a regular user.
    """
    user = attendee_factory.create()  # Creates a user in the database
    api_client.force_authenticate(user=user)
    api_client.user = user  # For easy access in tests
    return api_client


@pytest.fixture
def organizer_client(organizer_factory, api_client):
    user = organizer_factory.create()
    api_client.force_authenticate(user=user)
    api_client.user = user
    return api_client


# === SimpleJWT Specific Fixtures ===
# @pytest.fixture
# def expired_access_token(user_factory):
#     """
#     Returns an expired JWT access token for testing token expiration.
#     """
#     user = user_factory.create()
#     token = AccessToken.for_user(user)

#     past_time = timezone.now() - timedelta(seconds=10)
#     token["exp"] = int(past_time.timestamp())
#     return str(token)


@pytest.fixture
def invalid_access_token():
    """
    Returns a syntactically invalid JWT access token for testing validation errors.
    """
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
