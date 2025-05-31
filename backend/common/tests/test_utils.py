# import pytest
# # from common.choices import UserRole
# # from common.tests.factories import (
# #     BookingFactory,
# #     BookingItemFactory,
# #     EventFactory,
# #     TicketTypeFactory,
# #     UserFactory,
# # )
# # from rest_framework.test import APIClient
# # from rest_framework_simplejwt.tokens import RefreshToken

# print("✅ conftest.py loaded")


# @pytest.fixture
# def attendee_user():
#     """User with attendee role."""
#     from common.tests.factories import UserFactory
#     from common.choices import UserRole
#     return UserFactory(role=UserRole.ATTENDEE)


# @pytest.fixture
# def organizer_user():
#     """User with organizer role."""
#     from common.tests.factories import UserFactory
#     from common.choices import UserRole
#     return UserFactory(role=UserRole.ORGANIZER)


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


# # ------------------------
# # Clients
# # ------------------------


# @pytest.fixture
# def api_client():
#     """Base DRF APIClient without authentication."""
#     from rest_framework.test import APIClient
#     return APIClient()


# @pytest.fixture
# def attendee_client(attendee_user, api_client):
#     from rest_framework_simplejwt.tokens import RefreshToken
#     refresh = RefreshToken.for_user(attendee_user)
#     api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
#     return api_client


# @pytest.fixture
# def organizer_client(organizer_user, api_client):
#     from rest_framework_simplejwt.tokens import RefreshToken
#     refresh = RefreshToken.for_user(organizer_user)
#     api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
#     return api_client
