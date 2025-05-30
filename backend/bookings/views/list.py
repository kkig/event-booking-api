from bookings.models import Booking
from bookings.serializers import BookingDetailSerializer
from rest_framework import generics, permissions


class BookingListView(generics.ListAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("event")
            .prefetch_related(
                "items__ticket_type"
            )  # Optimized for one to many relationship
        )
