from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
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

    queryset = Event.objects.all()
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
    search_fields = ["title", "description"]

    # Allow sorting
    ordering_fields = ["start_time", "capacity", "created_at"]

    # Default odering
    odering = ["start_time"]

    def perform_create(self, serializer):
        """Called on POST request."""

        # Set the organizer to the logged-in user on create
        serializer.save(organizer=self.request.user)


class TicketTypeViewSet(viewsets.ModelViewSet):
    """
    Handle all the CRUD logic for the `TicketType`.

    `list`(GET), `retrieve`(GET by ID), `create`(POST),`update/partial_update`(PUT/PATCH), `destroy`(DELETE)
    """

    serializer_class = TicketTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk")
        return TicketType.objects.filter(event_id=event_id)

    def perform_create(self, serializer):
        event_id = self.kwargs.get("event_pk")
        event = Event.objects.get(pk=event_id)

        if event.organizer != self.request.user:
            raise PermissionDenied("You are not the organizer of this event.")

        serializer.save(event=event)
