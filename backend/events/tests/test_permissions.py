import pytest
from common.choices import EventStatus
from django.urls import reverse
from rest_framework import status

LIST_URL = reverse("events:event-list")
DETAIL_URL = "events:event-detail"

TICKET_TYPE_LIST = "events:event-ticket-types-list"
TICKET_TYPE_DETAIL = "events:event-ticket-types-detail"


# === Test Event Get permissions ===
DUMMY_EVENT_DATA = {
    "name": "New Concert",
    "description": "A rock concert",
    "start_time": "2025-12-25T19:00:00Z",
    "end_time": "2025-12-25T21:00:00Z",
    "location": "Stadium",
    "capacity": 5000,
    "status": EventStatus.UPCOMING,
}


@pytest.mark.django_db
def test_anon_request_list_event_return_200(api_client):
    response = api_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK


# === Test Event Create permissions ===
@pytest.mark.django_db
def test_organizer_request_create_event_return_201(organizer_client):
    response = organizer_client.post(LIST_URL, DUMMY_EVENT_DATA, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_attendee_request_create_event_return_403(attendee_client):
    response = attendee_client.post(LIST_URL, DUMMY_EVENT_DATA, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anon_request_create_event_return_401(api_client):
    response = api_client.post(LIST_URL, DUMMY_EVENT_DATA, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# === Test Event Retrieve permissions ===
@pytest.mark.django_db
def test_anon_request_retrieve_event_return_200(api_client, event_factory):
    event = event_factory()
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


# === Test Event Update permissions ===
DUMMY_EVENT_DATA_UPDATE = {"name": "Updated Concert Name"}


@pytest.mark.django_db
def test_organizer_request_update_event_return_200(organizer_client, event_factory):
    organizer = organizer_client.user
    event = event_factory(organizer=organizer)

    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = organizer_client.patch(url, DUMMY_EVENT_DATA_UPDATE, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_organizer_request_update_other_organizers_event_return_403(
    organizer_client, organizer_factory, event_factory
):

    other_organizer = organizer_factory()
    event = event_factory(organizer=other_organizer)
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = organizer_client.patch(url, DUMMY_EVENT_DATA_UPDATE, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_attendee_request_update_event_return_403(attendee_client, event_factory):
    event = event_factory()
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = attendee_client.patch(url, DUMMY_EVENT_DATA_UPDATE, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anon_request_update_event_return_401(api_client, event_factory):
    event = event_factory()
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = api_client.patch(url, DUMMY_EVENT_DATA_UPDATE, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# === Test Event Delete permissions ===
@pytest.mark.django_db
def test_organizer_request_delete_event_return_204(organizer_client, event_factory):
    organizer = organizer_client.user
    event = event_factory(organizer=organizer)
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = organizer_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_organizer_request_delete_other_organizers_event_return_403(
    organizer_client, organizer_factory, event_factory
):
    other_organizer = organizer_factory()
    event = event_factory(organizer=other_organizer)

    url = reverse(DETAIL_URL, kwargs={"pk": event.id})
    response = organizer_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_attendee_request_delete_event_return_403(attendee_client, event_factory):
    event = event_factory(organizer=attendee_client.user)
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = attendee_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anon_request_delete_event_return_401(api_client, event_factory):
    event = event_factory()
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# == Test Ticket Type List permissions ===
@pytest.mark.django_db
def test_anon_request_list_ticket_type_return_200(api_client, event_factory):
    event = event_factory()
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


# === Test Ticket Type Creation permissions ===
DUMMY_TICKET_TYPE_DATA = {
    "name": "Standard Ticket",
    "description": "This is test ticket type.",
    "price": 25.00,
    "quantity_available": 100,
}


@pytest.mark.django_db
def test_organizer_request_create_ticket_type_return_201(
    organizer_client, event_factory
):
    event = event_factory(organizer=organizer_client.user)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    DUMMY_TICKET_TYPE_DATA["event"] = event.id

    response = organizer_client.post(url, DUMMY_TICKET_TYPE_DATA, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_organizer_request_create_other_organizers_event_ticket_type_return_403(
    organizer_client, organizer_factory, event_factory
):
    """
    Test that organizer user can't create ticket type for other organizer's event.
    """
    other_organizer = organizer_factory()
    event = event_factory(organizer=other_organizer)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    DUMMY_TICKET_TYPE_DATA["event"] = event.id

    response = organizer_client.post(url, DUMMY_TICKET_TYPE_DATA, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_attendee_request_create_ticket_type_return_403(attendee_client, event_factory):
    event = event_factory(organizer=attendee_client.user)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    DUMMY_TICKET_TYPE_DATA["event"] = event.id

    response = attendee_client.post(url, DUMMY_TICKET_TYPE_DATA, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_anon_request_create_ticket_type_return_401(api_client, event_factory):
    event = event_factory()
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    DUMMY_TICKET_TYPE_DATA["event"] = event.id

    response = api_client.post(url, DUMMY_TICKET_TYPE_DATA, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
