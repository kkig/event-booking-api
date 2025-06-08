from bookings.models import Booking
from bookings.serializers import BookingDetailSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated


class BookingDetailView(RetrieveAPIView):
    serializer_class = BookingDetailSerializer

    # Avoid returning 403 - it prove that the given booking id exists
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Called right after view is initialized, before permission checks.
        Return 404 when there is no booking for the user.
        Otherwise pass filtered queryset(e.g., this user's bookings) to get_object().
        """
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("event")
            .prefetch_related(
                "items__ticket_type"
            )  # Optimizing booking.all() + booking.items.all() + item.ticket_type
        )
