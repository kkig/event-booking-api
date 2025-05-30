from bookings.models import Booking, BookingItem
from common.choices import BookingStatus
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from events.models import TicketType
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class BookingCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        "Cancel specified booking."
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

        if booking.status != BookingStatus.CONFIRMED:
            return Response(
                {"detail": "Booking already cancelled or invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Update booking status
            booking.status = BookingStatus.CANCELLED
            booking.save()

            # Get all booking items for a booking
            items = BookingItem.objects.filter(booking=booking).select_related(
                "ticket_type"
            )

            # Update ticket availability for each booking item
            for item in items:
                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_available=F("quantity_available") + item.quantity,
                    quantity_sold=F("quantity_sold") - item.quantity,
                )

        return Response({"detail": "Booking cancelled."}, status=status.HTTP_200_OK)
