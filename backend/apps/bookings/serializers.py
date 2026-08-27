from rest_framework import serializers

from apps.bookings.constants import BookingMessages
from apps.bookings.services import create_booking
from apps.events.models import TicketType

from .models import Booking, BookingItem


class BookingItemInputSerializer(serializers.Serializer):
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class BookingSerializer(serializers.Serializer):
    """
    Create new booking for an event after input validations.
    """

    # Field level validations
    # A booking can have many ticket types (e.g., Standard, Premium)
    event_id = serializers.IntegerField()
    items = BookingItemInputSerializer(many=True)

    def validate(self, data):
        """
        Lightweight validation. Non-concurrent sensitive.
        - Ticket types exist
        - Belong to the same event
        """
        event_id = data["event_id"]
        items = data["items"]

        # Get array of all ticket type ids
        ticket_type_ids = [item["ticket_type_id"] for item in items]

        # Get array of ticket type data from database
        # Django will SQL JOIN TicketType and event(FK) beforehand
        ticket_types = TicketType.objects.filter(id__in=ticket_type_ids).select_related(
            "event"
        )

        # Make sure all ticket types are available in database
        if len(ticket_types) != len(items):
            raise serializers.ValidationError(BookingMessages.INVALID_TICKET_TYPE)

        # All ticket types should be for the same event
        for tt in ticket_types:
            if tt.event.pk != event_id:
                raise serializers.ValidationError(
                    BookingMessages.INVALID_BOOK_FOR_EVENTS
                )

        data["ticket_type_ids"] = ticket_type_ids
        data["event"] = ticket_types[0].event

        return data

    def create(self, validated_data):
        """
        Called after object validation.
        """
        user = self.context["request"].user

        return create_booking(
            user=user,
            event_id=validated_data["event"].pk,
            items=validated_data["items"],
            ticket_type_ids=validated_data["ticket_type_ids"],
        )


class BookingItemSerializer(serializers.ModelSerializer):
    """Define response format for each booking item."""

    # Required field for request
    # source -> Get name field of ticket_type(FK) in BookingItem
    ticket_type_name = serializers.CharField(source="ticket_type.name", read_only=True)

    class Meta:
        model = BookingItem
        fields = ["id", "ticket_type_name", "quantity", "price_at_booking"]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Define response format for each booking."""

    # Get booking items where parent is current booking - booking.items.all()
    items = BookingItemSerializer(many=True)
    event_name = serializers.CharField(source="event.name", read_only=True)

    class Meta:
        model = Booking
        # Fields we want in response
        fields = [
            "booking_reference",
            "event_name",
            "status",
            "created_at",
            "updated_at",
            "items",
            "total_price",
        ]
