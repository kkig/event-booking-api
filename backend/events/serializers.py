from common.choices import EventStatus
from django.utils import timezone
from events.constants import EventMessages, TicketTypeMessages
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

    def validate_start_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(EventMessages.START_TIME_IS_PAST)
        return value

    def validate_end_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(EventMessages.END_TIME_IS_PAST)
        return value

    def validate_status(self, value):
        # Only allow 'upcoming' status on create
        if self.instance is None and value != EventStatus.UPCOMING:
            raise serializers.ValidationError(EventMessages.INVALID_STATUS_ON_CREATE)
        return value

    def validate(self, data):
        start = data.get("start_time", None)
        end = data.get("end_time", None)

        if end and start and end <= start:
            raise serializers.ValidationError(
                EventMessages.END_TIME_SHOULD_BE_AFTER_START
            )

        return data


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = [
            "id",
            "event",
            "name",
            "description",
            "price",
            "quantity_available",
            "quantity_sold",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "event", "created_at", "updated_at"]

    def validate_name(self, value):
        event = self.context.get("event")

        if event and TicketType.objects.filter(event=event, name=value).exists():
            raise serializers.ValidationError(
                TicketTypeMessages.DUPLICATE_NAME_FOR_THE_EVENT
            )
        return value

    def validate_quantity_available(self, value):
        """
        Only validate on creation.
        """
        if self.instance is None and value < 1:
            raise serializers.ValidationError(
                TicketTypeMessages.INVALID_AVAILABILITY_ON_CREATE
            )
        return value
