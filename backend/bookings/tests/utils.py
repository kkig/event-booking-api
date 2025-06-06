from bookings.serializers import BookingSerializer
from rest_framework.exceptions import ValidationError


def _attempt_booking(user, booking_data, success_list, error_list):
    """
    Attempt to create a booking for the given user and data.
    Appends to `success_list` or `error_list` depending on the outcome.
    """
    # Simulate request context
    request = type("Request", (), {"user": user})()
    context = {"request": request}

    serializer = BookingSerializer(data=booking_data, context=context)

    if serializer.is_valid():
        try:
            serializer.save()
            success_list.append(user.username)
        except ValidationError as e:
            error_list.append((user.username, str(e)))
    else:
        error_list.append((user.username, serializer.errors))
