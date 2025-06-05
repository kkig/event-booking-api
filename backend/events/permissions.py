from common.choices import UserRole
from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the event organizer to edit it.
    Others can only read.
    """

    def has_permission(self, request, view):
        """
        Called for every request before accessing a specific object.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow POST/PUT/PATCH/DELETE if user is organizer
        return getattr(request.user, "role", None) == UserRole.ORGANIZER

    def has_object_permission(self, request, view, obj):
        """
        Called when accessing a specific objec. (e.g., GET /events/42/)
        """
        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow only if the object belong to the user
        return obj.organizer == request.user
