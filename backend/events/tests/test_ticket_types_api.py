import pytest
from django.urls import reverse
from events.constants import TicketTypeMessages
from events.models import TicketType
from rest_framework import status

TICKET_TYPE_LIST = "events:event-ticket-types-list"
# TICKET_TYPE_DETAIL = "events:event-ticket-types-detail"

DUMMY_TICKET_TYPE_DATA = {
    "name": "Standard Ticket",
    "description": "This is test ticket type.",
    "price": 25.00,
    "quantity_available": 100,
    "is_active": True,
}

pytestmark = pytest.mark.django_db(transaction=True)


# === Test Ticket Type Validation ===
def test_create_ticket_type_with_valid_data(organizer_client, event_factory):
    organizer = organizer_client.user
    event = event_factory(organizer=organizer)

    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})
    payload = DUMMY_TICKET_TYPE_DATA.copy()
    payload["name"] = "Test ticket type"

    response = organizer_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Test ticket type"
    assert response.data["event"] == event.pk
    assert response.data["quantity_sold"] == 0
    assert TicketType.objects.filter(event=event, name="Test ticket type").exists()


@pytest.mark.parametrize(
    "field, value",
    [
        ("name", None),
        ("name", ""),
        ("name", "A" * 101),
        ("price", -25.00),
        ("quantity_available", 0),
        ("quantity_available", -10),
    ],
)
def test_create_ticket_type_with_invalid_data(
    field, value, organizer_client, event_factory
):
    """
    Test that organizer cannot create ticket type with invalid data.
    """
    event = event_factory(organizer=organizer_client.user)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    # Inject invalid field value
    invalid_data = DUMMY_TICKET_TYPE_DATA.copy()

    if value is None:
        invalid_data.pop(field, None)
    else:
        invalid_data[field] = value

    response = organizer_client.post(url, invalid_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_ticket_type_with_duplicate_name(
    organizer_client, event_factory, ticket_type_factory
):
    event = event_factory(organizer=organizer_client.user)
    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

    # Create a ticket type to ensure the name is already taken
    payload = DUMMY_TICKET_TYPE_DATA.copy()
    payload["name"] = "Test Premium"

    # Create the first ticket type
    ticket_type_factory(name="Test Premium", event=event)

    # Attempt to create a second ticket type with the same name
    response = organizer_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert TicketTypeMessages.DUPLICATE_NAME_FOR_THE_EVENT


# === Test List Ticket Types ===
def test_list_ticket_types_for_event(api_client, event_factory, ticket_type_factory):
    event = event_factory()
    ticket_type_factory(event=event, name="General", price=10.00)
    ticket_type_factory(event=event, name="Student", price=5.00)
    ticket_type_factory()  # Another ticket type for a different event

    url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.pk})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    results = response.data["results"]
    assert response.data["count"] == 2
    assert {item["name"] for item in results} == {"General", "Student"}
