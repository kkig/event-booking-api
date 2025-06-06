import threading

import pytest
from bookings.models import Booking
from bookings.serializers import BookingSerializer
from common.choices import BookingStatus
from django.urls import reverse

# Normally django_db use transaction rollback
# Allow real DB commit to enable select_for_update()
pytestmark = pytest.mark.django_db(transaction=True)

CREATE_URL = reverse("bookings:booking-create")


def _get_new_user_client(user, client):
    user = user.create()
    user_client = client()
    user_client.force_authenticate(user=user)
    user_client.user = user
    return user_client


def _attempt_booking(client, event_id, ticket_type_id, quantity, results, index):
    payload = {
        "event_id": event_id,
        "items": [{"ticket_type_id": ticket_type_id, "quantity": quantity}],
    }
    response = client.post(CREATE_URL, payload, format="json")
    results[index] = response


def test_concurrent_booking_edge_case(
    attendee_factory, ticket_type_factory, event_factory, api_client_factory
):
    event = event_factory(capacity=5)
    ticket_type = ticket_type_factory(event=event, quantity_available=5)

    # Create 2 different users to simulate real concurrent access
    client1 = _get_new_user_client(attendee_factory, api_client_factory)
    client2 = _get_new_user_client(attendee_factory, api_client_factory)
    assert client1.user != client2.user

    results = [None, None]

    # Both users try to book 3 tickets (3 + 3 > 5 = should cause one to fail)
    thread1 = threading.Thread(
        target=_attempt_booking,
        args=(client1, event.id, ticket_type.id, 3, results, 0),
    )
    thread2 = threading.Thread(
        target=_attempt_booking,
        args=(client2, event.id, ticket_type.id, 3, results, 1),
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

    def make_booking(user, index, results=results):
        request = api_client.post("/fake-booking/", data, format="json")
        request.user = user
        serializer = BookingSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            try:
                serializer.save()
                results[index] = "success"
            except Exception:
                results[index] = "failed"
        else:
            results[index] = "invalid"

    t1 = threading.Thread(target=make_booking, args=(user1, "user1"))
    t2 = threading.Thread(target=make_booking, args=(user2, "user2"))

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

    def book(data, user, label):
        request = api_client.post("/fake-booking/", data, format="json")
        request.user = user
        serializer = BookingSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            try:
                serializer.save()
                results[label] = "success"
            except Exception:
                results[label] = "failed"
        else:
            results[label] = "invalid"

    t1 = threading.Thread(target=book, args=(data1, user1, "user1"))
    t2 = threading.Thread(target=book, args=(data2, user2, "user2"))

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

    def user2_attempt():
        data = {
            "event_id": event.id,
            "items": [{"ticket_type_id": ticket_type.id, "quantity": 2}],
        }
        request = api_client.post("/fake-booking/", data, format="json")
        request.user = user2
        serializer = BookingSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            try:
                serializer.save()
                results["book"] = "success"
            except Exception:
                results["book"] = "failed"
        else:
            results["book"] = "invalid"

    cancel_thread = threading.Thread(target=cancel_user1_booking)
    book_thread = threading.Thread(target=user2_attempt)

    cancel_thread.start()
    cancel_thread.join()

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

    results = {}

    def book(user, label):
        data = {
            "event_id": event.id,
            "items": [{"ticket_type_id": ticket_type.id, "quantity": 2}],
        }
        request = api_client.post("/fake-booking/", data, format="json")
        request.user = user
        serializer = BookingSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            try:
                serializer.save()
                results[label] = "success"
            except Exception:
                results[label] = "failed"
        else:
            results[label] = "invalid"

    thread1 = threading.Thread(target=book, args=(user1, "user1"))
    thread2 = threading.Thread(target=book, args=(user2, "user2"))

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    assert sorted(results.values()) == ["failed", "success"]
    assert Booking.objects.filter(status=BookingStatus.CONFIRMED).count() == 1
