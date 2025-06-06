import pytest
from bookings.constants import BookingMessages
from bookings.models import Booking
from django.urls import reverse
from rest_framework import status

# from bookings.models import Booking

CREATE_URL = reverse("bookings:booking-create")


# === Test logics to create booking ===
@pytest.mark.django_db
def test_attendee_can_make_booking(ticket_type_factory, event_factory, attendee_client):
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
def test_public_cannot_make_booking(ticket_type_factory, event_factory, api_client):
    event = event_factory()
    ticket = ticket_type_factory.create(event=event)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 2}],
    }

    response = api_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_booking_with_multiple_ticket_types(
    attendee_client, event_factory, ticket_type_factory
):
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
def test_reject_ticket_type_with_different_events(
    attendee_client, event_factory, ticket_type_factory
):
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
    error_msg = f"Not enough tickets for {ticket.name}."
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_msg in response.data["non_field_errors"][0]


@pytest.mark.django_db
def test_quantity_equals_event_capacity(
    attendee_client, event_factory, ticket_type_factory
):
    event = event_factory()
    ticket = ticket_type_factory(event=event, quantity_available=event.capacity)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": event.capacity}],
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
    ticket2 = ticket_type_factory(event=event, quantity_available=event.capacity)

    payload = {
        "event_id": event.id,
        "items": [
            {"ticket_type_id": ticket1.id, "quantity": 1},
            {"ticket_type_id": ticket2.id, "quantity": event.capacity},
        ],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    error_msg = BookingMessages.QUANTITY_EXCEED_CAPACITY
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert error_msg in response.data["non_field_errors"][0]
