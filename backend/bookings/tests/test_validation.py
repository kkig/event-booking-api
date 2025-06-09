import pytest
from bookings.constants import BookingMessages
from bookings.models import Booking
from django.urls import reverse
from rest_framework import status

CREATE_URL = reverse("bookings:booking-create")


@pytest.mark.django_db
def test_can_make_booking(attendee_client, event_factory, ticket_type_factory):
    """
    Test that request succeeds.
    """
    event = event_factory(capacity=10)
    ticket = ticket_type_factory(event=event, quantity_available=10)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 2}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED


# === Input validation ===
@pytest.mark.django_db
def test_reject_no_ticket_type(attendee_client, event_factory):
    event = event_factory(capacity=10)

    payload = {"event_id": event.id}

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_reject_no_event_id(attendee_client, event_factory, ticket_type_factory):
    event = event_factory(capacity=10)
    ticket = ticket_type_factory(event=event, quantity_available=10)

    payload = {"items": [{"ticket_type_id": ticket.id, "quantity": 1}]}

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_reject_negative_ticket_quantity(
    attendee_client, event_factory, ticket_type_factory
):
    """
    Test that request rejects negative ticket quantity.
    """
    event = event_factory(capacity=10)
    ticket = ticket_type_factory(event=event, quantity_available=10)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": -1}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# === Serializer validation ===
@pytest.mark.django_db
def test_booking_with_multiple_ticket_types(
    attendee_client, event_factory, ticket_type_factory
):
    """
    Test that request succeeds when multiple ticket types belong to the same event.
    """
    event = event_factory()
    ticket1 = ticket_type_factory(event=event, name="VIP")
    ticket2 = ticket_type_factory(event=event, name="Standard")

    payload = {
        "event_id": event.id,
        "items": [
            {"ticket_type_id": ticket1.id, "quantity": 3},
            {"ticket_type_id": ticket2.id, "quantity": 2},
        ],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    user = attendee_client.user
    items = Booking.objects.get(user=user).items.all()  # type: ignore[attr-defined]

    assert items.count() == 2


@pytest.mark.django_db
def test_reject_multiple_entries_for_a_ticket_type(
    attendee_client, event_factory, ticket_type_factory
):
    """
    Test that request get rejected when there are multiple entries with the same ticket type.
    """
    event = event_factory(capacity=10)
    ticket = ticket_type_factory(event=event, quantity_available=10, name="Standard")

    payload = {
        "event_id": event.id,
        "items": [
            # Multiple entries for the same ticket type
            {"ticket_type_id": ticket.id, "quantity": 2},
            {"ticket_type_id": ticket.id, "quantity": 1},
        ],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_reject_ticket_type_for_different_events(
    attendee_client, event_factory, ticket_type_factory
):
    """
    Test that when request gets rejected when it has ticket types for different events.
    All ticket type entries should belong to the same event.
    """
    event = event_factory()
    event_another = event_factory()
    ticket = ticket_type_factory(event=event)
    ticket_another = ticket_type_factory(event=event_another)

    payload = {
        "event_id": event.id,
        "items": [
            {"ticket_type_id": ticket.id, "quantity": ticket.quantity_available - 1},
            {
                "ticket_type_id": ticket_another.id,
                "quantity": ticket_another.quantity_available - 1,
            },
        ],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    error_msg = BookingMessages.INVALID_BOOK_FOR_EVENTS
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_msg in response.data["non_field_errors"][0]


@pytest.mark.django_db
def test_reject_invalid_ticket_type(attendee_client, event_factory):
    event = event_factory(capacity=10)

    payload = {"event_id": event.id, "items": [{"ticket_type_id": 5, "quantity": 1}]}

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
