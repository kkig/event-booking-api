from rest_framework import permissions, viewsets

from .models import Event
from .serializers import EventSerializer


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the event organizer to edit it.
    Others can only read.
    """

    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow only if the object belong to the user
        return obj.organizer == request.user


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

    def perform_create(self, serializer):
        """Called on POST request."""

        # Set the organizer to the logged-in user on create
        serializer.save(organizer=self.request.user)
