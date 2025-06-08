import pytest
from django.urls import reverse
from rest_framework import status

CREATE_URL = reverse("bookings:booking-create")


# === Auth validation ===


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
