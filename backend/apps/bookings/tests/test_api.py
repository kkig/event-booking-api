import pytest
from django.urls import reverse_lazy
from rest_framework import status

from apps.common.choices import BookingStatus

LIST_URL = reverse_lazy("bookings:my-bookings")
RETRIEVE_BASE = "bookings:booking-detail"
CANCEL_BASE = "bookings:booking-cancel"


# === Test List views ===
@pytest.mark.django_db
def test_user_get_result_list(attendee_client, booking_factory):
    booking_factory(user=attendee_client.user, with_items=2)
    booking_factory(user=attendee_client.user, with_items=1)

    response = attendee_client.get(LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2


@pytest.mark.django_db
def test_user_with_no_booking_get_empty_result(attendee_client):
    response = attendee_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


# === Test Retrieval views ===
@pytest.mark.django_db
def test_user_get_booking_detail(attendee_client, booking_factory):
    booking = booking_factory(user=attendee_client.user, with_items=3)
    url = reverse_lazy(
        RETRIEVE_BASE, kwargs={"booking_reference": booking.booking_reference}
    )

    response = attendee_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    result = response.data
    assert result["booking_reference"] == str(booking.booking_reference)
    assert result["event_name"] == booking.event.name
    assert result["status"] == booking.status
    assert result["total_price"] == str(booking.total_price)


@pytest.mark.django_db
def test_user_with_no_booking_get_404(attendee_client):
    url = reverse_lazy(
        RETRIEVE_BASE, kwargs={"booking_reference": 9999}
    )  # Non-existent booking ID

    response = attendee_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# === Test Cancel Booking ===
@pytest.mark.django_db
def test_user_cancel_booking(attendee_client, booking_factory):
    booking = booking_factory(user=attendee_client.user, status=BookingStatus.CONFIRMED)
    url = reverse_lazy(
        CANCEL_BASE, kwargs={"booking_reference": booking.booking_reference}
    )

    response = attendee_client.put(url)
    assert response.status_code == status.HTTP_200_OK

    booking.refresh_from_db()
    assert booking.status == BookingStatus.CANCELLED


@pytest.mark.django_db
def test_user_cancel_will_update_ticket_availability(
    attendee_client, booking_item_factory, ticket_type_factory
):
    ticket_type = ticket_type_factory(quantity_available=10, quantity_sold=5)
    booking_item = booking_item_factory(
        booking__user=attendee_client.user, ticket_type=ticket_type, quantity=2
    )

    url = reverse_lazy(
        CANCEL_BASE,
        kwargs={"booking_reference": booking_item.booking.booking_reference},
    )

    response = attendee_client.put(url)
    assert response.status_code == status.HTTP_200_OK

    ticket_type.refresh_from_db()
    assert ticket_type.quantity_available == 12  # 10 + 2 from booking item
    assert ticket_type.quantity_sold == 3  # 5 - 2 from booking item
