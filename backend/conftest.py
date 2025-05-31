from datetime import timedelta

import pytest

# Import factories
from bookings.tests.factories import BookingFactory, BookingItemFactory
from common.tests.factories import AttendeeFactory, OrganizerFactory, UserFactory
from django.utils import timezone
from events.tests.factories import EventFactory, TicketTypeFactory
from pytest_factoryboy import register
from rest_framework_simplejwt.tokens import AccessToken

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
    from rest_framework.test import APIClient

    return APIClient()


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
@pytest.fixture
def jwt_authenticated_client(api_client, user_factory):
    """
    Return an API client authenticated with a valid JWT access token.
    This simulates a real JWT flow, processing headers via SimpleJWT's backend
    """
    user = user_factory.create()
    access_token = str(AccessToken.for_user(user))
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    api_client.user = user  # Attach user for convinience
    return api_client


@pytest.fixture
def jwt_organizer_client(api_client, organizer_factory):
    """
    Return an API client authenticated as an organizer with a valid JWT access token.
    """
    organizer = organizer_factory.create()
    access_token = str(AccessToken.for_user(organizer))
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    api_client.user = organizer  # Attach user for convinience
    return api_client


@pytest.fixture
def expired_access_token(user_factory):
    """
    Returns an expired JWT access token for testing token expiration.
    """
    user = user_factory.create()
    token = AccessToken.for_user(user)

    past_time = timezone.now() - timedelta(seconds=10)
    token["exp"] = int(past_time.timestamp())
    return str(token)


@pytest.fixture
def invalid_access_token():
    """
    Returns a syntactically invalid JWT access token for testing validation errors.
    """
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
