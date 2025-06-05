import pytest
from common.choices import EventStatus, UserRole


@pytest.mark.django_db
def test_event_creation(event_factory):
    """
    Test that event created via EventFactory has required fields.
    """
    event = event_factory()

    assert event.id is not None
    assert event.name.startswith("Test Event")
    assert event.description is not None
    assert event.location is not None
    assert event.capacity == 100
    assert event.organizer.role == UserRole.ORGANIZER
    assert event.status == EventStatus.UPCOMING


@pytest.mark.django_db
def test_ticket_type_creation(ticket_type_factory):
    """
    Test that ticket type created via TicketTypeFactory has required fields.
    """
    ticket_type = ticket_type_factory()

    assert ticket_type.id is not None
    assert ticket_type.event.name.startswith("Test Event")
    assert ticket_type.name.startswith("Ticket")
    assert ticket_type.description == "General Admission"
    assert ticket_type.price is not None
    assert ticket_type.quantity_available is not None
    assert ticket_type.quantity_sold == 0


def test_event_str_representation(event_factory):
    """
    Test __str__ method of Event model.
    """
    event = event_factory.build()

    assert str(event).startswith("Test Event")


def test_ticket_type_str_representation(ticket_type_factory):
    """
    Test __str__ method of TicketType model.
    """
    ticket_type = ticket_type_factory.build()

    assert str(ticket_type).startswith(f"{ticket_type.event.name} - ")
