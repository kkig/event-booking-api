from rest_framework.permissions import BasePermission


class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "organizer"


class IsAttendee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "attendee"
