from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAttendee
from apps.bookings.filters import BookingFilter
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingDetailSerializer


class BookingListView(ListAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated, IsAttendee]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_queryset(self):
        # For documentation tools
        if getattr(self, "swagger_fake_view", False):
            return Booking.objects.none()

        return (
            # Optimized for one to many relationship
            Booking.objects.filter(user=self.request.user)
            .select_related("event")
            .prefetch_related("items__ticket_type")
            .order_by("-created_at")
        )
