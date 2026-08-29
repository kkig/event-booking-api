from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.bookings.constants import BookingMessages
from apps.bookings.models import Booking, BookingItem
from apps.common.choices import BookingStatus
from apps.events.models import Event, TicketType


@transaction.atomic
def create_booking(*, user, event_id, items, ticket_type_ids):
    """
    Create a confirmed booking atomically.

    The Event row is locked first to serialize bookings competing
    for the same event capacity. TicketType rows are then locked
    to protect per-ticket inventory.
    """
    event = Event.objects.select_for_update().get(pk=event_id)

    locked_ticket_types = (
        TicketType.objects.select_for_update()
        .filter(id__in=ticket_type_ids)
        .order_by("id")
    )

    ticket_map = {ticket_type.pk: ticket_type for ticket_type in locked_ticket_types}

    if len(ticket_map) != len(ticket_type_ids):
        raise ValidationError(BookingMessages.INVALID_TICKET_TYPE)

    total_requested = sum(item["quantity"] for item in items)

    if event.total_tickets_sold + total_requested > event.total_capacity:
        raise ValidationError(BookingMessages.QUANTITY_EXCEED_CAPACITY)

    for item in items:
        ticket_type = ticket_map[item["ticket_type_id"]]
        quantity = item["quantity"]

        if not ticket_type.is_active:
            raise ValidationError(BookingMessages.INACTIVE_TICKET_TYPE)

        if ticket_type.quantity_available < quantity:
            raise ValidationError(BookingMessages.NOT_ENOUGH_TICKETS)

    total_price = sum(
        item["quantity"] * ticket_map[item["ticket_type_id"]].price for item in items
    )

    booking = Booking.objects.create(
        user=user,
        event=event,
        status=BookingStatus.CONFIRMED,
        total_price=total_price,
    )

    for item in items:
        ticket_type = ticket_map[item["ticket_type_id"]]
        quantity = item["quantity"]

        BookingItem.objects.create(
            booking=booking,
            ticket_type=ticket_type,
            quantity=quantity,
            price_at_booking=ticket_type.price,
        )

        ticket_type.quantity_available = F("quantity_available") - quantity
        ticket_type.quantity_sold = F("quantity_sold") + quantity
        ticket_type.save(update_fields=["quantity_available", "quantity_sold"])

    return booking


@transaction.atomic
def cancel_booking(*, user, booking_reference):
    """
    Cancel a booking atomically.
    """
    booking = get_object_or_404(
        Booking.objects.select_for_update(),
        user=user,
        booking_reference=booking_reference,
    )

    if booking.status != BookingStatus.CONFIRMED:
        raise ValidationError(BookingMessages.INVALID_STATUS_TO_CANCEL)

    items = list(
        BookingItem.objects.filter(booking=booking)
        .select_related("ticket_type")
        .order_by("ticket_type_id")
    )

    # Lock inventory rows before restoring quantities.
    ticket_type_ids = [item.ticket_type.pk for item in items]

    list(
        TicketType.objects.select_for_update()
        .filter(pk__in=ticket_type_ids)
        .order_by("pk")
    )

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=["status", "cancelled_at"])

    for item in items:
        TicketType.objects.filter(pk=item.ticket_type.pk).update(
            quantity_available=F("quantity_available") + item.quantity,
            quantity_sold=F("quantity_sold") - item.quantity,
        )

    return booking
