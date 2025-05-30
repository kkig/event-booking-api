from rest_framework import generics, permissions

from backend.bookings.models import Booking
from backend.bookings.serializers import BookingDetailSerializer


class BookingListView(generics.ListAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("event")
            .prefetch_related(
                "items__ticket_type"
            )  # Optimized for many to many relationship
        )
