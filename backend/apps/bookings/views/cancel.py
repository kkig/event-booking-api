from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAttendee
from apps.bookings.constants import BookingMessages
from apps.bookings.services import cancel_booking


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated, IsAttendee]

    @extend_schema(
        request=None,
        responses=inline_serializer(
            name="BookingCancelResponse",
            fields={
                "detail": serializers.CharField(),
            },
        ),
    )
    def put(self, request, *args, **kwargs):
        """
        Cancel specified booking.
        """
        cancel_booking(
            user=request.user,
            booking_reference=kwargs["booking_reference"],
        )

        return Response(
            {"detail": BookingMessages.CANCELLED_SUCCESSFULLY},
            status=status.HTTP_200_OK,
        )
