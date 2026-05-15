from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.permissions import IsOrganizer
from apps.bookings.models import Booking
from apps.common.choices import BookingStatus, EventStatus
from apps.events.constants import EventMessages

from .models import Event, TicketType
from .permissions import IsOrganizerOrReadOnly
from .serializers import EventSerializer, TicketTypeSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    Handle all the CRUD logic.

    GET /           - List all events.
    POST /          - Create new event.
    GET /{id}/      - Retrieve event by ID.
    PUT/PATCH /{id}/ - Update event by ID.
    DELETE /{id}/   - Delete event by ID.
    """

    queryset = Event.objects.all().order_by("created_at")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Simple exact-match filters
    filterset_fields = ["status", "location"]

    # Free-text search
    search_fields = ["name", "description"]

    # Allow sorting
    ordering_fields = ["start_time", "total_capacity", "created_at"]

    # Default ordering
    ordering = ["start_time"]

    def perform_create(self, serializer):
        """Called on POST request."""

        # Set the organizer to the logged-in user on create
        serializer.save(organizer=self.request.user)

    def perform_update(self, serializer):
        # Fetches the current event instance before the update
        old_event = self.get_object()
        old_status = old_event.status

        # Applies the updates (e.g., updates the event in the DB)
        updated_event = serializer.save()

        is_updated = old_status != updated_event.status
        is_cancelled = updated_event.status == EventStatus.CANCELLED

        if is_updated and is_cancelled:
            now = timezone.now()
            # Cancel related bookings
            bookings = list(Booking.objects.filter(event=updated_event))
            for booking in bookings:
                booking.status = BookingStatus.CANCELLED
                booking.cancelled_at = now
            Booking.objects.bulk_update(bookings, ["status", "cancelled_at"])

            # Deactivate ticket types
            TicketType.objects.filter(event=updated_event).update(is_active=False)


class TicketTypeViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Handle ticket types for an event.
    GET /events/{event_pk}/ticket-types/ - List all ticket types for an event.
    POST /events/{event_pk}/ticket-types/ - Create a new ticket type for an event.
    """

    serializer_class = TicketTypeSerializer
    permission_classes = [permissions.IsAuthenticated]  # Default fallback

    def get_permissions(self):
        """
        Set permissions based on action.
        - List: Read-only for all users.
        - Create: Only organizers can create ticket types.
        """
        if self.action == "list":
            return [permissions.AllowAny()]
        elif self.action == "create":
            return [permissions.IsAuthenticated(), IsOrganizer()]
        return super().get_permissions()  # fallback to permission_classes

    def get_queryset(self):
        """
        Return ticket types for the specific event.
        """
        event_id = self.kwargs.get("event_pk")
        return TicketType.objects.filter(event_id=event_id).order_by("id")

    def get_serializer_context(self):
        """
        Pass event to serializer for validation and read-only logic.
        """
        context = super().get_serializer_context()
        event_id = self.kwargs.get("event_pk")
        if event_id:
            try:
                context["event"] = Event.objects.get(pk=event_id)
            except Event.DoesNotExist:
                context["event"] = None
        return context

    def perform_create(self, serializer):
        """
        Called on POST request to create a new ticket type.
        Ensures the user is the organizer of the event.
        """
        event_id = self.kwargs.get("event_pk")
        event = Event.objects.get(pk=event_id)

        if event.organizer != self.request.user:
            raise PermissionDenied(EventMessages.NOT_EVENT_OWNER)

        serializer.save(event=event)
