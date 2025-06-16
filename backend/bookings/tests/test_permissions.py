import pytest
from django.urls import reverse
from rest_framework import status

CREATE_URL = reverse("bookings:booking-create")
LIST_URL = reverse("bookings:my-bookings")
RETRIEVE_BASE = "bookings:booking-detail"
CANCEL_BASE = "bookings:booking-cancel"


# === Test Create ===
@pytest.mark.django_db
def test_attendee_can_make_booking(ticket_type_factory, event_factory, attendee_client):
    event = event_factory(total_capacity=10)
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
    event = event_factory(total_capacity=10)
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


# === Test List ===
@pytest.mark.django_db
def test_attendee_can_get_own_booking_list(attendee_client, booking_factory):
    booking = booking_factory(user=attendee_client.user)
    response = attendee_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert booking.id == response.data["results"][0]["id"]


@pytest.mark.django_db
def test_attendee_cannot_get_others_booking_list(attendee_client, booking_factory):
    booking = booking_factory()
    assert booking.user != attendee_client.user

    response = attendee_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_anon_user_cannot_get_booking_list(api_client, booking_factory):
    booking_factory()

    response = api_client.get(LIST_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_organizer_cannot_get_booking_list(organizer_client, booking_factory):
    booking_factory()

    response = organizer_client.get(LIST_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# === Test Retrieve ===
@pytest.mark.django_db
def test_attendee_can_view_own_booking(attendee_client, booking_factory):
    booking = booking_factory(user=attendee_client.user)
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    assert attendee_client.user == booking.user

    response = attendee_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_anon_user_cannot_see_booking(api_client, booking_factory):
    booking = booking_factory()
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_attendee_cannot_see_others_booking(attendee_client, booking_factory):
    booking = booking_factory()
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    assert attendee_client.user != booking.user

    response = attendee_client.get(url)

    # Queried booking not found in this user's bookings
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_organizer_cannot_see_booking(organizer_client, booking_factory):
    booking = booking_factory()
    url = reverse(RETRIEVE_BASE, kwargs={"pk": booking.pk})

    assert organizer_client.user != booking.user

    response = organizer_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# === Test Cancel ===
@pytest.mark.django_db
def test_attendee_can_cancel_booking(attendee_client, booking_factory):
    booking = booking_factory(user=attendee_client.user)
    url = reverse(CANCEL_BASE, kwargs={"pk": booking.id})

    response = attendee_client.put(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_attendee_cannot_cancel_others_booking(attendee_client, booking_factory):
    booking = booking_factory()
    assert booking.user != attendee_client.user

    url = reverse(CANCEL_BASE, kwargs={"pk": booking.id})
    response = attendee_client.put(url)

    # The booking not found in this attendee requester's bookings
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_anon_cannot_cancel_booking(api_client, booking_factory):
    booking = booking_factory()
    url = reverse(CANCEL_BASE, kwargs={"pk": booking.id})
    response = api_client.put(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_organizer_cannot_cancel_booking(organizer_client, booking_factory):
    booking = booking_factory()
    assert booking.user != organizer_client.user

    url = reverse(CANCEL_BASE, kwargs={"pk": booking.id})
    response = organizer_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
