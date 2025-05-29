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
            "title",
            "description",
            "location",
            "start_time",
            "end_time",
            "capacity",
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
            "quantity",
            "quantity_available",
            "created_at",
        ]
        read_only_fields = ["id", "quantity_available", "created_at", "event"]
