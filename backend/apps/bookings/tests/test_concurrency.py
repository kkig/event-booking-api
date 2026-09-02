import threading

import pytest
from django.urls import reverse_lazy
from rest_framework import status

from apps.bookings.models import Booking
from apps.bookings.tests.utils import threaded_booking
from apps.common.choices import BookingStatus

# Normally django_db use transaction rollback
# Allow real DB commit to enable select_for_update()
pytestmark = pytest.mark.django_db(transaction=True)

CREATE_URL = reverse_lazy("bookings:booking-create")


def test_concurrent_booking_edge_case(
    attendee_factory, ticket_type_factory, event_factory, api_client_factory
):
    event = event_factory(total_capacity=5)
    ticket_type = ticket_type_factory(event=event, quantity_available=5)

    user1 = attendee_factory.create()
    user2 = attendee_factory.create()

    client1 = api_client_factory()
    client1.force_authenticate(user=user1)

    client2 = api_client_factory()
    client2.force_authenticate(user=user2)

    data = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket_type.id, "quantity": 3}],
    }

    barrier = threading.Barrier(2)
    results = [None, None]

    def make_booking(client, index):
        barrier.wait()
        results[index] = client.post(CREATE_URL, data, format="json")

    thread1 = threading.Thread(target=make_booking, args=(client1, 0))
    thread2 = threading.Thread(target=make_booking, args=(client2, 1))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    responses = [resp for resp in results if resp is not None]

    successes = [resp for resp in responses if resp.status_code == 201]
    failures = [resp for resp in responses if resp.status_code == 400]

    assert len(successes) == 1
    assert len(failures) == 1
    assert "capacity" in failures[0].json()[0].lower()


def test_concurrent_exact_last_ticket_booking(
    attendee_factory, event_factory, ticket_type_factory, api_client_factory
):
    """
    When 2 users try to book the last ticket for the same event,
    only one of them can make booking.
    """
    event = event_factory(total_capacity=1)
    ticket_type = ticket_type_factory(
        event=event, quantity_available=1, quantity_sold=0
    )

    user1 = attendee_factory.create()
    user2 = attendee_factory.create()

    client1 = api_client_factory()
    client1.force_authenticate(user=user1)

    client2 = api_client_factory()
    client2.force_authenticate(user=user2)

    data = {
        "event_id": event.id,
        "items": [{"ticket_type_id": ticket_type.id, "quantity": 1}],
    }

    barrier = threading.Barrier(2)
    results = [None, None]

    def make_booking(client, index):
        barrier.wait()
        results[index] = client.post(CREATE_URL, data, format="json")

    thread1 = threading.Thread(target=make_booking, args=(client1, 0))
    thread2 = threading.Thread(target=make_booking, args=(client2, 1))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    responses = [resp for resp in results if resp is not None]

    successes = [resp for resp in responses if resp.status_code == 201]
    failures = [resp for resp in responses if resp.status_code == 400]

    assert len(successes) == 1
    assert len(failures) == 1
    assert Booking.objects.count() == 1


def test_concurrent_shared_event_capacity(
    attendee_factory, ticket_type_factory, event_factory, api_client
):
    """
    When 2 users try to book for the same event and that will exceed
    event capacity, only one of them can make booking.
    """
    event = event_factory(total_capacity=5)

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


def test_concurrent_cancellation_only_restores_inventory_once(
    attendee_factory,
    booking_factory,
    ticket_type_factory,
    event_factory,
    api_client_factory,
):
    """
    When two requests try to cancel the same booking simultaneously,
    only one cancellation should succeed and inventory should be restored once.
    """
    event = event_factory(total_capacity=2)
    ticket_type = ticket_type_factory(
        event=event, quantity_available=0, quantity_sold=2
    )

    user = attendee_factory.create()

    booking = booking_factory(user=user, event=event, status=BookingStatus.CONFIRMED)
    booking.items.create(
        ticket_type=ticket_type, quantity=2, price_at_booking=ticket_type.price
    )

    cancel_url = reverse_lazy(
        "bookings:booking-cancel",
        kwargs={"booking_reference": booking.booking_reference},
    )

    client1 = api_client_factory()
    client1.force_authenticate(user=user)

    client2 = api_client_factory()
    client2.force_authenticate(user=user)

    barrier = threading.Barrier(2)
    results = []

    def cancel(client):
        barrier.wait()
        response = client.put(cancel_url)
        results.append(response)

    thread1 = threading.Thread(target=cancel, args=(client1,))
    thread2 = threading.Thread(target=cancel, args=(client2,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    assert len(results) == 2

    statuses = sorted(response.status_code for response in results)

    assert statuses == [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    booking.refresh_from_db()
    ticket_type.refresh_from_db()

    assert booking.status == BookingStatus.CANCELLED
    assert booking.cancelled_at is not None

    # Inventory must be restored exactly once.
    assert ticket_type.quantity_available == 2
    assert ticket_type.quantity_sold == 0


def test_simultaneous_booking_only_one_succeeds(
    attendee_factory, ticket_type_factory, event_factory, api_client
):
    """
    Prevent overbooking when 2 users try to book for the same event
    at the same time.
    """
    event = event_factory(total_capacity=2)
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
