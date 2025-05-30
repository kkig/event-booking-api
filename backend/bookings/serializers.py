from common.choices import BookingStatus
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Sum
from events.models import TicketType
from rest_framework import serializers

from .models import Booking, BookingItem


class BookingSerializer(serializers.Serializer):
    # Field level validation
    # Required fields for booking request
    event_id = serializers.IntegerField()
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        """Object level validation. Do cross-field or context-aware checks."""
        try:
            # Django will SQL JOIN TicketType and event(FK) beforehand
            # Get TicketType and event(FK) in one query
            ticket_type = TicketType.objects.select_related("event").get(
                id=data["ticket_type_id"]
            )
        except TicketType.DoesNotExist:
            raise serializers.ValidationError("Ticket type does not exist.")

        # Prevents from booking a ticket for wrong event
        if ticket_type.event.pk != data["event_id"]:
            raise serializers.ValidationError(
                "Ticket type does not belong to the specified event."
            )

        # Check availability - pre-check and avoids DB work
        if ticket_type.quantity_available < data["quantity"]:
            raise serializers.ValidationError("Not enough tickets available.")

        # Check event capacity
        event = ticket_type.event
        total_sold = (
            TicketType.objects.filter(event=event).aggregate(
                total=Sum("quantity_sold")
            )["total"]
            or 0
        )
        if total_sold + data["quantity"] > event.capacity:
            raise serializers.ValidationError(
                "Booking this quantity would exceed the event's capacity."
            )

        return data

    def create(self, validated_data):
        """Called after object validation."""
        user = self.context["request"].user
        quantity = validated_data["quantity"]
        ticket_type_id = validated_data["ticket_type_id"]

        # Complete successfully or do nothing (atomicity)
        with transaction.atomic():
            # Row locking for concurrency (pessimistic lock)
            # Prevents race conditions
            ticket_type = TicketType.objects.select_for_update().get(id=ticket_type_id)
            event = ticket_type.event

            # Re-check capacity inside transaction to prevent race conditions
            total_sold = (
                TicketType.objects.select_for_update()
                .filter(event=event)
                .aggregate(total=Sum("quantity_sold"))["total"]
                or 0
            )
            if total_sold + quantity > event.capacity:
                raise ValidationError("Booking this would exceed the event's capacity.")

            # Check availability (2nd) - critical check for consistency
            if ticket_type.quantity_available < quantity:
                raise ValidationError("Not enough tickets available.")

            ticket_type.quantity_available = F("quantity_available") - quantity
            ticket_type.quantity_sold = F("quantity_sold") + quantity
            ticket_type.save()

            booking = Booking.objects.create(
                user=user,
                event_id=validated_data["event_id"],
                status=BookingStatus.CONFIRMED,
            )

            BookingItem.objects.create(
                booking=booking, ticket_type=ticket_type, quantity=quantity
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
    event_name = serializers.CharField(source="event.title", read_only=True)

    class Meta:
        model = Booking
        # Fields we want in response
        fields = ["id", "event_name", "status", "created_at", "items"]
