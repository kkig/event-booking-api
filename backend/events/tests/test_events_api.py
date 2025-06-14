from datetime import timedelta

import pytest
from common.choices import EventStatus
from django.urls import reverse
from django.utils import timezone
from events.models import Event
from rest_framework import status

LIST_URL = reverse("events:event-list")
DETAIL_URL = "events:event-detail"

pytestmark = pytest.mark.django_db(transaction=True)


# === POST and PUT Validation ===
EVENT_START_TIME = timezone.now() + timedelta(days=14)
EVENT_END_TIME = timezone.now() + timedelta(days=14, hours=2)

DUMMY_EVENT_DATA = {
    "name": "New Concert",
    "description": "A rock concert",
    "start_time": EVENT_START_TIME,
    "end_time": EVENT_END_TIME,
    "location": "Stadium",
    "total_capacity": 5000,
    "status": EventStatus.UPCOMING,
}


class TestEventValidations:
    def test_create_event_with_valid_data(self, organizer_client):
        payload = DUMMY_EVENT_DATA.copy()
        payload["organizer"] = organizer_client.user.id

        start_time = payload["start_time"].isoformat(timespec="microseconds") + "Z"
        end_time = payload["end_time"].isoformat(timespec="microseconds") + "Z"

        response = organizer_client.post(LIST_URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["name"] == payload["name"]
        assert response.data["description"] == payload["description"]

        # Compare up to seconds
        assert response.data["start_time"].startswith(start_time[:19])
        assert response.data["end_time"].startswith(end_time[:19])
        assert response.data["location"] == payload["location"]
        assert response.data["total_capacity"] == payload["total_capacity"]
        assert response.data["status"] == payload["status"]
        assert response.data["organizer"] == str(organizer_client.user)

    def test_create_event_without_optional_fields(self, organizer_client):
        payload = DUMMY_EVENT_DATA.copy()
        payload.pop("end_time", None)
        payload.pop("description", None)
        payload.pop("status", None)

        response = organizer_client.post(LIST_URL, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "field, value",
        [
            ("name", None),  # Missing name field
            ("name", ""),  # Empty name
            ("name", "A" * 256),  # Name too long
            ("start_time", None),  # Missing time
            ("start_time", EVENT_START_TIME - timedelta(days=30)),
            ("end_time", EVENT_START_TIME),  # start time != end time
            (
                "end_time",
                EVENT_START_TIME - timedelta(days=1),
            ),  # End time before start time
            ("location", None),
            ("location", "A" * 256),
            ("total_capacity", 0),  # Zero capacity
            ("total_capacity", -100),
            ("status", "INVALID_STATUS"),  # Invalid status
            ("status", EventStatus.PAST),  # Invalid status for creation
        ],
    )
    def test_create_event_with_invalid_data(self, field, value, organizer_client):
        """
        Test that organizer cannot create event with invalid data.
        """
        # Inject invalid value
        invalid_data = DUMMY_EVENT_DATA.copy()
        if value is None:
            invalid_data.pop(field, None)  # Simulate missing field
        else:
            invalid_data[field] = value

        invalid_data["organizer"] = organizer_client.user.id

        # Attempt to create event with invalid data
        response = organizer_client.post(LIST_URL, invalid_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data


# === Test Event Get API ===
def test_get_event_list(api_client, event_factory):
    """
    Test that GET returns a list of events.
    """
    event1 = event_factory(name="Test Event 1", status=EventStatus.UPCOMING)
    event2 = event_factory(name="Test Event 2", status=EventStatus.UPCOMING)
    response = api_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    result = response.data["results"]
    assert result[0]["id"] == event1.id
    assert result[1]["id"] == event2.id
    assert result[0]["name"] == event1.name
    assert result[1]["name"] == event2.name


def test_get_list_with_no_events(api_client):
    """
    Test that GET returns empty list when no events exist.
    """
    response = api_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


# === Test Event Create Views ===
def test_create_event(organizer_client):
    """
    Test that organizer can create event.
    """
    organizer = organizer_client.user
    payload = DUMMY_EVENT_DATA.copy()
    response = organizer_client.post(LIST_URL, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    event_name = payload["name"]

    assert Event.objects.filter(name=event_name, organizer=organizer).exists()
    assert response.data["organizer"] == str(organizer)


# === Test Event Detail Views ===
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


class TestEventFiltering:
    def test_filter_events_by_filterset(self, api_client, event_factory):
        """
        Test the we can filter events by location.
        """
        event1 = event_factory(location="Stadium", status=EventStatus.UPCOMING)
        event_factory(location="Arena", status=EventStatus.UPCOMING)

        response = api_client.get(LIST_URL, {"location": "Stadium"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == event1.id

    def test_filter_events_by_text_search(self, api_client, event_factory):
        """
        Test that we can filter events by test search.
        """
        event1 = event_factory(name="Katamari Rock", status=EventStatus.UPCOMING)
        _ = event_factory(name="Katamari Pop", status=EventStatus.UPCOMING)

        response = api_client.get(LIST_URL, {"search": "Rock"})
        results = response.data["results"]

        assert response.status_code == status.HTTP_200_OK
        assert len(results) == 1
        assert results[0]["name"] == event1.name

    def test_filter_events_by_ordering(self, api_client, event_factory):
        """
        Test that we can order events by capacity.
        """
        event1 = event_factory(name="Event A", total_capacity=800)
        event2 = event_factory(name="Event B", total_capacity=500)
        response = api_client.get(LIST_URL, {"ordering": "capacity"})
        results = response.data["results"]

        assert response.status_code == status.HTTP_200_OK
        assert len(results) == 2
        assert results[0]["name"] == event1.name
        assert results[1]["name"] == event2.name
