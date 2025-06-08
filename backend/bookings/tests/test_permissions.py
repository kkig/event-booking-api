import pytest
from django.urls import reverse
from rest_framework import status

CREATE_URL = reverse("bookings:booking-create")
RETRIEVE_BASE = "bookings:booking-detail"


# === Create ===


@pytest.mark.django_db
def test_attendee_can_make_booking(ticket_type_factory, event_factory, attendee_client):
    event = event_factory(capacity=10)
    ticket = ticket_type_factory(event=event, quantity_available=10)

    # Required fields for serializer
    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 2}],
    }

    response = attendee_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_organizer_cannot_make_booking(
    organizer_client, event_factory, ticket_type_factory
):
    event = event_factory(capacity=10)
    ticket = ticket_type_factory(event=event, quantity_available=10)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 2}],
    }
    response = organizer_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anon_user_cannot_make_booking(ticket_type_factory, event_factory, api_client):
    event = event_factory()
    ticket = ticket_type_factory.create(event=event)

    payload = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket.id, "quantity": 2}],
    }

    response = api_client.post(CREATE_URL, payload, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# === Retrieve ===


@pytest.mark.django_db
def test_attendee_can_view_own_booking(attendee_client, booking_factory):
    booking = booking_factory(user=attendee_client.user)
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    assert attendee_client.user == booking.user

    response = attendee_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_anon_user_cannot_see_booking(api_client, booking_factory):
    booking = booking_factory()
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    response = api_client.get(url, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_attendee_cannot_see_others_booking(attendee_client, booking_factory):
    booking = booking_factory()
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    assert attendee_client.user != booking.user

    response = attendee_client.get(url, format="json")

    # Queried booking not found in this user's bookings
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_organizer_cannot_see_booking(organizer_client, booking_factory):
    booking = booking_factory()
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    assert organizer_client.user != booking.user

    resopnse = organizer_client.get(url, format="json")
    assert resopnse.status_code == status.HTTP_404_NOT_FOUND
