import pytest
from django.urls import reverse
from rest_framework import status

LIST_URL = reverse("events:event-list")
DETAIL_URL = "events:event-detail"

TICKET_TYPE_LIST = "events:event-ticket-types-list"
TICKET_TYPE_DETAIL = "events:event-ticket-types-detail"

# # === Test Ticket Type Validation ===
# @pytest.mark.parametrize(
#     "field, value",
#     [
#         ("name", None),
#         ("name", ""),
#         ("name", "A" * 101),
#         ("price", -25.00),
#         ("quantity_available", -10),
#         ("quantity_available", 0),
#     ],
# )
# def test_create_ticket_type_with_invalid_data(
#     field, value, organizer_client, event_factory
# ):
#     """
#     Test that organizer cannot create ticket type with invalid data.
#     """
#     event = event_factory(organizer=organizer_client.user)
#     url = reverse(TICKET_TYPE_LIST, kwargs={"event_pk": event.id})

#     valid_data = {
#         "name": "Standard Ticket",
#         "description": "This is test ticket type.",
#         "price": 25.00,
#         "quantity_available": 100,
#         "quantity_sold": 0,
#         "is_active": True,
#     }

#     # Inject invalid field value
#     invalid_data = valid_data.copy()
#     if value is None:
#         invalid_data.pop(field, None)
#     else:
#         invalid_data[field] = value

#     response = organizer_client.post(url, invalid_data, format="json")
#     assert response.status_code == status.HTTP_400_BAD_REQUEST


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
