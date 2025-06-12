from rest_framework import serializers

from .models import Event, TicketType


class EventSerializer(serializers.ModelSerializer):
    # Organizer is auto-assigned from logged-in user
    organizer = serializers.ReadOnlyField(source="organizer.username")

    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "name",
            "description",
            "location",
            "start_time",
            "end_time",
            "total_capacity",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organizer", "created_at", "updated_at"]


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = [
            "id",
            "event",
            "name",
            "description",
            "price",
            "quantity_sold",
            "quantity_available",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "event"]
