from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsAttendee
from apps.bookings.constants import BookingMessages
from apps.bookings.services import cancel_booking


class BookingCancelView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAttendee]

    def update(self, request, *args, **kwargs):
        """
        Cancel specified booking.
        """
        cancel_booking(user=request.user, booking_reference=kwargs["booking_reference"])

        return Response(
            {"detail": BookingMessages.CANCELLED_SUCCESSFULLY},
            status=status.HTTP_200_OK,
        )
