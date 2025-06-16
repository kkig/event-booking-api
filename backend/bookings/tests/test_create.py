import pytest
from bookings.constants import BookingMessages
from bookings.models import Booking
from django.urls import reverse
from rest_framework import status

CREATE_URL = reverse("bookings:booking-create")


# === Test logics to create booking ===
@pytest.mark.django_db
def test_attendees_booking_adds_to_database(
    ticket_type_factory, event_factory, attendee_client
):
    event = event_factory()
    ticket = ticket_type_factory.create(event=event)

    # Required fields for serializer
    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 2}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    user = attendee_client.user
    booking = Booking.objects.get(user=user)
    assert booking.items.count() == 1  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_booking_ticket_updates_ticket_type_quantity(
    attendee_client, event_factory, ticket_type_factory
):
    event = event_factory()
    ticket = ticket_type_factory(event=event, quantity_available=10, quantity_sold=0)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 3}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    ticket.refresh_from_db()
    assert ticket.quantity_available == 7
    assert ticket.quantity_sold == 3


@pytest.mark.django_db
def test_ticket_type_with_enough_availability(
    attendee_client, event_factory, ticket_type_factory
):
    event = event_factory()
    ticket = ticket_type_factory(event=event)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 1}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_ticket_type_availability_equals_request_quantity(
    attendee_client, event_factory, ticket_type_factory
):
    event = event_factory()
    ticket = ticket_type_factory(event=event)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": ticket.quantity_available}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    user = attendee_client.user
    booking = Booking.objects.get(user=user)
    assert booking.items.count() == 1  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_quantity_exceeds_ticket_type_availability(
    attendee_client, event_factory, ticket_type_factory
):
    event = event_factory()
    ticket = ticket_type_factory(event=event)

    payload = {
        "event_id": event.id,
        "items": [
            {"ticket_type_id": ticket.id, "quantity": ticket.quantity_available + 1}
        ],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    error_msg = f"Not enough tickets for: {ticket.name}."
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_msg in response.data


@pytest.mark.django_db
def test_quantity_equals_event_capacity(
    attendee_client, event_factory, ticket_type_factory
):
    event = event_factory()
    ticket = ticket_type_factory(event=event, quantity_available=event.total_capacity)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": event.total_capacity}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    user = attendee_client.user
    booking = Booking.objects.get(user=user)
    assert booking.items.count() == 1  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_total_quantity_exceeds_event_capacity(
    attendee_client, event_factory, ticket_type_factory
):
    event = event_factory()
    ticket1 = ticket_type_factory(event=event)
    ticket2 = ticket_type_factory(event=event, quantity_available=event.total_capacity)

    payload = {
        "event_id": event.id,
        "items": [
            {"ticket_type_id": ticket1.id, "quantity": 1},
            {"ticket_type_id": ticket2.id, "quantity": event.total_capacity},
        ],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    error_msg = BookingMessages.QUANTITY_EXCEED_CAPACITY
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_msg in response.data
