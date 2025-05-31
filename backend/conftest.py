import pytest

# Import factories
from common.tests.factories import AttendeeFactory, OrganizerFactory, UserFactory
from pytest_factoryboy import register

# Register the factories as fixtures
# By default, the fixture name will be the lowercase class name
register(UserFactory)
register(OrganizerFactory)
register(AttendeeFactory)


# @pytest.fixture
# def sample_event(organizer_user):
#     from common.tests.factories import EventFactory
#     return EventFactory(organizer=organizer_user)


# @pytest.fixture
# def ticket_type(sample_event):
#     from common.tests.factories import TicketTypeFactory
#     return TicketTypeFactory(event=sample_event)


# @pytest.fixture
# def booking(attendee_user, sample_event):
#     from common.tests.factories import BookingFactory
#     return BookingFactory(user=attendee_user, event=sample_event)


# @pytest.fixture
# def booking_item(booking, ticket_type):
#     from common.tests.factories import BookingItemFactory
#     return BookingItemFactory(booking=booking, ticket_type=ticket_type)


# ------------------------
# Clients
# ------------------------


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
    return api_client


@pytest.fixture
def organizer_client(organizer_factory, api_client):
    user = organizer_factory.create()
    api_client.force_authenticate(user=user)
    return api_client
