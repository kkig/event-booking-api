import pytest
from django.urls import reverse
from rest_framework import status

LIST_URL = reverse("bookings:my-bookings")


# === Test List views ===
@pytest.mark.django_db
def test_user_get_result_list(attendee_client, booking_factory):
    booking = booking_factory(user=attendee_client.user)

    response = attendee_client.get(LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    result = response.data["results"][0]

    assert booking.id == result["id"]
    assert booking.event.name == result["event_name"]
    assert booking.status == result["status"]


@pytest.mark.django_db
def test_user_with_no_booking_get_empty_result(attendee_client):
    response = attendee_client.get(LIST_URL)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0
