from bookings.constants import BookingMessages
from common.choices import BookingStatus
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from events.models import TicketType
from rest_framework import serializers

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
        Object level validation.
        Do cross-field or context-aware checks.
        """
        event_id = data["event_id"]
        items = data["items"]

        # Get array of all ticket type ids
        ticket_type_ids = [item["ticket_type_id"] for item in items]
        self._ticket_type_ids = ticket_type_ids

        # Get array of ticket type data from database
        ticket_types = TicketType.objects.filter(id__in=ticket_type_ids).select_related(
            "event"
        )  # Django will SQL JOIN TicketType and event(FK) beforehand

        # Make sure all ticket types are available in database
        if len(ticket_types) != len(items):
            raise serializers.ValidationError(BookingMessages.INVALID_TICKET_TYPE)

        # All ticket types should be for the same event
        for tt in ticket_types:
            if tt.event.pk != event_id:
                raise serializers.ValidationError(
                    BookingMessages.INVALID_BOOK_FOR_EVENTS
                )

        # Make sure requested ticket type quantity don't exceed its availability
        ticket_type_map = {tt.pk: tt for tt in ticket_types}
        for item in items:
            tt = ticket_type_map[item["ticket_type_id"]]
            if tt.quantity_available < item["quantity"]:
                raise serializers.ValidationError(f"Not enough tickets for {tt.name}.")

        # Make sure total quantity requested don't exceed event capacity
        event = ticket_types[0].event
        total_requested = sum(item["quantity"] for item in items)
        total_sold = event.total_tickets_sold

        self._total_requested = total_requested

        if total_requested + total_sold > event.capacity:
            raise serializers.ValidationError(BookingMessages.QUANTITY_EXCEED_CAPACITY)

        return data

    def create(self, validated_data):
        """
        Called after object validation.
        """
        user = self.context["request"].user
        items = validated_data["items"]

        # Complete successfully or do nothing (atomicity)
        with transaction.atomic():
            # Row locking for concurrency (pessimistic lock)
            # Prevents race conditions

            ticket_type_ids = self._ticket_type_ids

            # Lock all ticket types
            ticket_types = TicketType.objects.select_for_update().filter(
                id__in=ticket_type_ids
            )
            # Make mapping of ticket type id to its data
            ticket_type_map = {tt.pk: tt for tt in ticket_types}

            # Re-check capacity inside transaction to prevent race conditions
            event = ticket_types[0].event
            total_sold = event.total_tickets_sold
            total_requested = self._total_requested

            if total_sold + total_requested > event.capacity:
                raise ValidationError(BookingMessages.QUANTITY_EXCEED_CAPACITY)

            # Create booking
            booking = Booking.objects.create(
                user=user,
                event=event,
                status=BookingStatus.CONFIRMED,
            )

            # Create booking items + update stock
            for item in items:
                tt = ticket_type_map[item["ticket_type_id"]]
                quantity = item["quantity"]

                if tt.quantity_available < quantity:
                    raise ValidationError(
                        f"Not enough tickets available for: {tt.name}"
                    )

                # Update quantities
                tt.quantity_available = F("quantity_available") - quantity
                tt.quantity_sold = F("quantity_sold") + quantity
                tt.save()

                # Create item
                BookingItem.objects.create(
                    booking=booking,
                    ticket_type=tt,
                    quantity=quantity,
                )

        return booking


class BookingItemSerializer(serializers.ModelSerializer):
    """Define response format for each booking item."""

    # Required field for request
    # source -> Get name field of ticket_type(FK) in BookingItem
    ticket_type_name = serializers.CharField(source="ticket_type.name", read_only=True)

    class Meta:
        model = BookingItem
        fields = ["id", "ticket_type_name", "quantity"]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Define response format for each booking."""

    # Get booking items where parent is current booking - booking.items.all()
    items = BookingItemSerializer(many=True)
    event_name = serializers.CharField(source="event.name", read_only=True)

    class Meta:
        model = Booking
        # Fields we want in response
        fields = ["id", "event_name", "status", "created_at", "items"]
