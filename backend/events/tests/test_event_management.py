import pytest
from common.choices import EventStatus
from django.urls import reverse
from events.models import Event, TicketType
from rest_framework import status

LIST_URL = reverse("events:event-list")
DETAIL_URL = "events:event-detail"

TICKET_TYPE_LIST = "events:event-ticket-types-list"
TICKET_TYPE_DETAIL = "events:event-ticket-types-detail"


DUMMY_EVENT_DATA = {
    "name": "New Concert",
    "description": "A rock concert",
    "start_time": "2025-12-25T19:00:00Z",
    "end_time": "2025-12-25T21:00:00Z",
    "location": "Stadium",
    "capacity": 5000,
    "status": EventStatus.UPCOMING,
}


# === Test Event Creation ===
@pytest.mark.django_db
def test_organizer_can_create_event(organizer_client):
    """
    Test that organizer can create event.
    """
    organizer = organizer_client.user
    response = organizer_client.post(LIST_URL, DUMMY_EVENT_DATA, format="json")

    assert response.status_code == 201
    assert Event.objects.filter(name="New Concert", organizer=organizer).exists()
    assert response.data["organizer"] == str(organizer)


@pytest.mark.django_db
def test_attendee_cannot_create_event(attendee_client):
    """
    Test that attendee can't create event.
    """
    response = attendee_client.post(LIST_URL, DUMMY_EVENT_DATA, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_event(api_client):
    """
    Test that unauthenticated user can't create event.
    """
    response = api_client.post(LIST_URL, DUMMY_EVENT_DATA, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_organizer_can_update_their_event(organizer_client, event_factory):
    """
    Test that organizer can update their event.
    """
    organizer = organizer_client.user
    event = event_factory(organizer=organizer)
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})
    data = {"name": "Updated Concert Name"}
    response = organizer_client.patch(url, data, format="json")
    event.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert event.name == "Updated Concert Name"


@pytest.mark.django_db
def test_organizer_cannot_update_other_organizers_event(
    organizer_client, organizer_factory, event_factory
):
    """
    Test that organizer can't update other organizer's event.
    """
    other_organizer = organizer_factory()
    event = event_factory(organizer=other_organizer)
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})
    data = {"name": "Attempted Update"}
    response = organizer_client.patch(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_organizer_can_delete_their_event(organizer_client, event_factory):
    """
    Test that organizer can delete their event.
    """
    organizer = organizer_client.user
    event = event_factory(organizer=organizer)
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})
    response = organizer_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Event.objects.filter(id=event.id).exists()


@pytest.mark.django_db
def test_public_can_view_event_list(api_client, event_factory):
    """
    Test that public can view event list.
    """
    event_factory.create_batch(3)
    response = api_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) >= 3


@pytest.mark.django_db
def test_public_can_view_event_details(api_client, event_factory):
    """
    Test that public can view event detail.
    """
    event = event_factory()
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == event.name


@pytest.mark.django_db
def test_organizer_can_create_ticket_type(organizer_client, event_factory):
    """
    Test that organizer can create ticket type.
    """
    event = event_factory(organizer=organizer_client.user)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})
    data = {
        "event": event.id,  # Ensure event is included in data if serializer requires it
        "name": "Standard Ticket",
        "description": "This is test ticket type.",
        "price": 25.00,
        "quantity_available": 100,
    }
    response = organizer_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert TicketType.objects.filter(event=event, name="Standard Ticket").exists()


@pytest.mark.django_db
def test_organizer_cannot_create_ticket_type_for_other_organizers_event(
    organizer_client, organizer_factory, event_factory
):
    """
    Test that organizer user can't create ticket type for other organizer's event.
    """
    other_organizer = organizer_factory()
    event = event_factory(organizer=other_organizer)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})
    data = {
        "event": event.id,
        "name": "Standard Ticket",
        "description": "This is test ticket type.",
        "price": 25.00,
        "quantity_available": 100,
    }
    response = organizer_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
