import pytest
from common.choices import EventStatus
from django.urls import reverse
from events.models import Event
from rest_framework import status

LIST_URL = reverse("events:event-list")
DETAIL_URL = "events:event-detail"

TICKET_TYPE_LIST = "events:event-ticket-types-list"
TICKET_TYPE_DETAIL = "events:event-ticket-types-detail"


# === Test Event Get Views ===
@pytest.mark.django_db
def test_get_event_list(api_client, event_factory):
    """
    Test that GET returns a list of events.
    """
    event = event_factory(name="Test Event 1", status=EventStatus.UPCOMING)
    response = api_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    result = response.data["results"][0]
    assert result["id"] == event.id
    assert result["name"] == event.name


@pytest.mark.django_db
def test_get_list_with_multiple_events(api_client, event_factory):
    """
    Test that GET returns a list of events.
    """
    event_factory.create_batch(3)
    response = api_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) >= 3


@pytest.mark.django_db
def test_get_list_with_no_events(api_client):
    """
    Test that GET returns empty list when no events exist.
    """
    response = api_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


# === Test Event Filter Views ===
@pytest.mark.django_db
def test_filter_events_by_filterset(api_client, event_factory):
    """
    Test the we can filter events by location.
    """
    event1 = event_factory(location="Stadium", status=EventStatus.UPCOMING)
    event_factory(location="Arena", status=EventStatus.UPCOMING)

    response = api_client.get(LIST_URL, {"location": "Stadium"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == event1.id


@pytest.mark.django_db
def test_filter_events_by_text_search(api_client, event_factory):
    """
    Test that we can filter events by test search.
    """
    event1 = event_factory(name="Katamari Rock", status=EventStatus.UPCOMING)
    event2 = event_factory(name="Katamari Pop", status=EventStatus.UPCOMING)
    response = api_client.get(LIST_URL, {"search": "katamari"})
    results = response.data["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(results) == 2
    assert results[0]["name"] in (event1.name, event2.name)


@pytest.mark.django_db
def test_filter_events_by_ordering(api_client, event_factory):
    """
    Test that we can order events by capacity.
    """
    event = event_factory(
        name="Event A", total_capacity=800, status=EventStatus.UPCOMING
    )
    event_factory(name="Event B", total_capacity=500, status=EventStatus.UPCOMING)
    response = api_client.get(LIST_URL, {"ordering": "capacity"})
    results = response.data["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(results) == 2
    assert results[0]["name"] == event.name


# == Test Event Create Validation ===
@pytest.mark.django_db
def test_create_event_with_invalid_data(organizer_client):
    """
    Test that organizer cannot create event with invalid data.
    """
    invalid_data = {"name": "", "description": "A rock concert"}

    response = organizer_client.post(LIST_URL, invalid_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# === Test Event Create Views ===
DUMMY_EVENT_DATA = {
    "name": "New Concert",
    "description": "A rock concert",
    "start_time": "2025-12-25T19:00:00Z",
    "location": "Stadium",
    "total_capacity": 5000,
    "status": EventStatus.UPCOMING,
}


@pytest.mark.django_db
def test_create_event(organizer_client):
    """
    Test that organizer can create event.
    """
    organizer = organizer_client.user
    response = organizer_client.post(LIST_URL, DUMMY_EVENT_DATA, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    event_name = DUMMY_EVENT_DATA["name"]

    assert Event.objects.filter(name=event_name, organizer=organizer).exists()
    assert response.data["organizer"] == str(organizer)


# === Test Event Detail Views ===
@pytest.mark.django_db
def test_view_event_details(api_client, event_factory):
    """
    Test that public can view event detail.
    """
    event = event_factory()
    url = reverse(DETAIL_URL, kwargs={"pk": event.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == event.name


# === Test Event Update Views ===
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


# === Test Event Delete Views ===
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


# === Test Ticket Type Validation ===
@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "name": "",  # Empty name
            "description": "This is test ticket type.",
            "price": 25.00,
            "quantity_available": 100,
        },
        {
            "name": "Standard Ticket",
            "description": "This is test ticket type.",
            "price": -25.00,  # Negative price
            "quantity_available": 100,
        },
        {
            "name": "Standard Ticket",
            "description": "This is test ticket type.",
            "price": 25.00,
            # "quantity_available": 0,  # Zero quantity
        },
    ],
)
def test_create_ticket_type_with_invalid_data(
    invalid_data, organizer_client, event_factory
):
    """
    Test that organizer cannot create ticket type with invalid data.
    """
    event = event_factory(organizer=organizer_client.user)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    event_id = None if "event" in invalid_data else event.id
    invalid_data["event"] = event_id  # Ensure event is included

    response = organizer_client.post(url, invalid_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


DUMMY_TICKET_TYPE_DATA = {
    "name": "Standard Ticket",
    "description": "This is test ticket type.",
    "price": 25.00,
    "quantity_available": 100,
}


# @pytest.mark.django_db
# def test_create_ticket_type_with_duplicate_name(
#     organizer_client, event_factory, ticket_type_factory
# ):
#     event = event_factory(organizer=organizer_client.user, status=EventStatus.UPCOMING)
#     url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

#     # Create a ticket type to ensure the name is already taken
#     payload = {
#         "name": "Duplicate Ticket",
#         "description": "This is a test ticket type.",
#         "price": 20.00,
#         "quantity_available": 50.0,
#     }

#     # Create the first ticket type
#     ticket_type_factory(**payload)

#     # Attempt to create a second ticket type with the same name
#     response = organizer_client.post(url, payload, format="json")
#     assert response.status_code == status.HTTP_400_BAD_REQUEST


# # === Test Ticket Type Create Views ===
# @pytest.mark.django_db
# def test_organizer_can_create_ticket_type(organizer_client, event_factory):
#     """
#     Test that organizer can create ticket type.
#     """
#     event = event_factory(organizer=organizer_client.user)
#     url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})
#     data = {
#         "event": event.id,  # Ensure event is included in data if serializer requires it
#         "name": "Standard Ticket",
#         "description": "This is test ticket type.",
#         "price": 25.00,
#         "quantity_available": 100,
#     }
#     response = organizer_client.post(url, data, format="json")

#     assert response.status_code == status.HTTP_201_CREATED
#     assert TicketType.objects.filter(event=event, name="Standard Ticket").exists()


# @pytest.mark.django_db
# def test_organizer_cannot_create_ticket_type_for_other_organizers_event(
#     organizer_client, organizer_factory, event_factory
# ):
#     """
#     Test that organizer user can't create ticket type for other organizer's event.
#     """
#     other_organizer = organizer_factory()
#     event = event_factory(organizer=other_organizer)
#     url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})
#     data = {
#         "event": event.id,
#         "name": "Standard Ticket",
#         "description": "This is test ticket type.",
#         "price": 25.00,
#         "quantity_available": 100,
#     }
#     response = organizer_client.post(url, data, format="json")
#     assert response.status_code == status.HTTP_403_FORBIDDEN


# @pytest.mark.django_db
# def test_event_does_not_allow_overselling(event_factory, ticket_type_factory):
#     """
#     Test that we can't sell exceeding capacity.
#     """
#     event = event_factory(capacity=10)
#     ticket_type = ticket_type_factory(event=event, quantity_available=10)

#     # Simulate 10 tickets sold
#     ticket_type.quantity_sold = 10
#     ticket_type.save()

#     assert event.total_tickets_sold == 10

#     # Try to 'sell' one more (simulate overbooking)
#     ticket_type.quantity_sold += 1
#     ticket_type.save()

#     event.refresh_from_db()
#     assert event.total_tickets_sold > event.capacity
