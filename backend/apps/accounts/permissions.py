from rest_framework.permissions import BasePermission

from apps.common.choices import UserRole


class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ORGANIZER


class IsAttendee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ATTENDEE
