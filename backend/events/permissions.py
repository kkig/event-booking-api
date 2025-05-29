from rest_framework import permissions


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
