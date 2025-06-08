import threading

import pytest
from bookings.models import Booking
from bookings.tests.utils import api_booking_attempt, threaded_booking
from common.choices import BookingStatus
from django.urls import reverse

# Normally django_db use transaction rollback
# Allow real DB commit to enable select_for_update()
pytestmark = pytest.mark.django_db(transaction=True)

CREATE_URL = reverse("bookings:booking-create")


def test_concurrent_booking_edge_case(
    attendee_factory, ticket_type_factory, event_factory, api_client_factory
):
    event = event_factory(capacity=5)
    ticket_type = ticket_type_factory(event=event, quantity_available=5)

    # Create new clients
    user1 = attendee_factory.create()
    user2 = attendee_factory.create()
    assert user1 != user2

    client1 = api_client_factory()
    client1.force_authenticate(user=user1)
    client1.user = user1

    client2 = api_client_factory()
    client2.force_authenticate(user=user2)
    client2.user = user2

    assert client1 != client2

    results = [None, None]

    # Both users try to book 3 tickets (3 + 3 > 5 = should cause one to fail)
    thread1 = threading.Thread(
        target=lambda: results.__setitem__(
            0, api_booking_attempt(client1, event.id, ticket_type.id, 3)
        ),
    )
    thread2 = threading.Thread(
        target=lambda: results.__setitem__(
            1, api_booking_attempt(client2, event.id, ticket_type.id, 3)
        )
    )

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Check: only one success, the other fails
    successes = [resp for resp in results if resp and resp.status_code == 201]
    failures = [resp for resp in results if resp and resp.status_code == 400]

    assert len(successes) == 1, "Exactly one booking should succeed."
    assert len(failures) == 1, "Exactly one booking should fail."
    assert "capacity" in failures[0].json()[0].lower()


def test_concurrent_exact_last_ticket_booking(
    attendee_factory, event_factory, ticket_type_factory, api_client
):
    """
    When 2 users try to book the last ticket for the same event,
    only one of them can make booking.
    """
    event = event_factory(capacity=1)
    ticket_type = ticket_type_factory(
        event=event, quantity_available=1, quantity_sold=0
    )

    user1 = attendee_factory.create()
    user2 = attendee_factory.create()
    assert user1 != user2

    data = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket_type.id, "quantity": 1}],
    }

    results = {}

    t1 = threading.Thread(
        target=threaded_booking, args=(user1, data, "user1", results, api_client)
    )
    t2 = threading.Thread(
        target=threaded_booking, args=(user2, data, "user2", results, api_client)
    )

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert sorted(results.values()) == ["failed", "success"]
    assert Booking.objects.count() == 1


def test_concurrent_shared_event_capacity(
    attendee_factory, ticket_type_factory, event_factory, api_client
):
    """
    When 2 users try to book for the same event and that will exceed
    event capacity, only one of them can make booking.
    """
    event = event_factory(capacity=5)

    standard = ticket_type_factory(event=event, quantity_available=5, name="Standard")
    vip = ticket_type_factory(event=event, quantity_available=5, name="VIP")

    user1 = attendee_factory()
    user2 = attendee_factory()

    data1 = {
        "event_id": event.id,
        "items": [{"ticket_type_id": standard.id, "quantity": 3}],
    }
    data2 = {
        "event_id": event.id,
        "items": [{"ticket_type_id": vip.id, "quantity": 3}],
    }

    results = {}

    t1 = threading.Thread(
        target=threaded_booking, args=(user1, data1, "user1", results, api_client)
    )
    t2 = threading.Thread(
        target=threaded_booking, args=(user2, data2, "user2", results, api_client)
    )

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert "success" in results.values()
    assert "failed" in results.values()
    assert Booking.objects.count() == 1


def test_concurrent_booking_after_cancellation(
    user_factory, booking_factory, ticket_type_factory, event_factory, api_client
):
    """
    When user canceled booking, it should free up tickets
    and another user can to book the tickets.
    """
    event = event_factory(capacity=2)
    ticket_type = ticket_type_factory(event=event, quantity_available=2)

    user1 = user_factory.create()
    user2 = user_factory.create()
    assert user1 != user2

    booking1 = booking_factory(user=user1, event=event, status=BookingStatus.CONFIRMED)
    booking1.items.create(ticket_type=ticket_type, quantity=2)
    assert Booking.objects.filter(status=BookingStatus.CONFIRMED).count() == 1

    # Simulate fully booked
    ticket_type.quantity_available = 0
    ticket_type.quantity_sold = 2
    ticket_type.save()

    # Results store
    results = {}

    def cancel_user1_booking():
        # Simulate cancellation logic
        booking1.status = BookingStatus.CANCELLED
        booking1.save()

        # Restore ticket availability manually here for test
        ticket_type.refresh_from_db()
        ticket_type.quantity_available = 2
        ticket_type.quantity_sold = 0
        ticket_type.save()

        results["cancel"] = "done"

    cancel_thread = threading.Thread(target=cancel_user1_booking)
    cancel_thread.start()
    cancel_thread.join()

    data = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket_type.id, "quantity": 2}],
    }

    book_thread = threading.Thread(
        target=threaded_booking, args=(user2, data, "book", results, api_client)
    )
    book_thread.start()
    book_thread.join()

    assert results["cancel"] == "done"
    assert results["book"] == "success"
    assert Booking.objects.filter(status=BookingStatus.CONFIRMED).count() == 1


def test_simultaneous_booking_only_one_succeeds(
    attendee_factory, ticket_type_factory, event_factory, api_client
):
    """
    Prevent overbooking when 2 users try to book for the same event
    at the same time.
    """
    event = event_factory(capacity=2)
    ticket_type = ticket_type_factory(event=event, quantity_available=2)

    user1 = attendee_factory.create()
    user2 = attendee_factory.create()

    data = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket_type.id, "quantity": 2}],
    }

    results = {}

    thread1 = threading.Thread(
        target=threaded_booking, args=(user1, data, "user1", results, api_client)
    )
    thread2 = threading.Thread(
        target=threaded_booking, args=(user2, data, "user2", results, api_client)
    )

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    assert sorted(results.values()) == ["failed", "success"]
    assert Booking.objects.filter(status=BookingStatus.CONFIRMED).count() == 1
