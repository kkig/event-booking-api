from accounts.permissions import IsAttendee
from bookings.models import Booking, BookingItem
from common.choices import BookingStatus
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from events.models import TicketType
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class BookingCancelView(UpdateAPIView):
    serializer_class = None
    permission_classes = [IsAuthenticated, IsAttendee]
    queryset = Booking.objects.all()

    def get_object(self):
        booking = get_object_or_404(
            Booking.objects.filter(user=self.request.user).prefetch_related(
                "items__ticket_type"
            ),
            # From URL parameters
            pk=self.kwargs.get("pk"),
        )

        if booking.status != BookingStatus.CONFIRMED:
            raise ValidationError("Booking already cancelled or invalid status.")

        return booking

    def update(self, request, *args, **kwargs):
        """
        Cancel specified booking.
        """
        booking = self.get_object()

        with transaction.atomic():
            # Update booking status
            booking.status = BookingStatus.CANCELLED
            booking.save()

            # Get all booking items for a booking
            items = BookingItem.objects.filter(booking=booking)

            # Update ticket availability for each booking item
            for item in items:
                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_available=F("quantity_available") + item.quantity,
                    quantity_sold=F("quantity_sold") - item.quantity,
                )

        return Response({"detail": "Booking cancelled."}, status=status.HTTP_200_OK)
