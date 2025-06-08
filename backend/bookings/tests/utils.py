from bookings.serializers import BookingSerializer
from django.urls import reverse
from rest_framework.exceptions import ValidationError

CREATE_URL = reverse("bookings:booking-create")


def simulate_booking_request(user, data, api_client):
    request = api_client.post("/fake-booking/", data, format="json")
    request.user = user
    serializer = BookingSerializer(data=data, context={"request": request})

    if serializer.is_valid():
        try:
            serializer.save()
            return "success"

        except ValidationError:
            return "failed"

    else:
        return "invalid"


def threaded_booking(user, data, label, results, api_client):
    result = simulate_booking_request(user, data, api_client)
    results[label] = result


def api_booking_attempt(client, event_id, ticket_type_id, quantity):
    payload = {
        "event_id": event_id,
        "items": [{"ticket_type_id": ticket_type_id, "quantity": quantity}],
    }
    return client.post(CREATE_URL, payload, format="json")
