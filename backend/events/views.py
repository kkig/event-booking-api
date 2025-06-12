from accounts.permissions import IsOrganizer
from django_filters.rest_framework import DjangoFilterBackend
from events.constants import EventMessages
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

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


class TicketTypeViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Handle ticket types for an event.
    GET /events/{event_pk}/ticket-types/ - List all ticket types for an event.
    POST /events/{event_pk}/ticket-types/ - Create a new ticket type for an event.
    """

    serializer_class = TicketTypeSerializer

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

    def get_queryset(self):
        """
        Return ticket types for the specific event.
        """
        event_id = self.kwargs.get("event_pk")
        return TicketType.objects.filter(event_id=event_id).order_by("id")

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
