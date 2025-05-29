from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from .models import Event
from .permissions import IsOrganizerOrReadOnly
from .serializers import EventSerializer


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
