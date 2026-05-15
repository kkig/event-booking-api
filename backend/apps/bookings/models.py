import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.choices import BookingStatus
from apps.events.models import Event, TicketType

User = get_user_model()


class Booking(models.Model):
    """User's reservation for an event."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING
    )
    booking_reference = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]  # Most recent booking first

    def __str__(self):
        return f"Booking {self.booking_reference} by {self.user.username} for {self.event.name}"


class BookingItem(models.Model):
    """Specific ticket type and quantity for a booking."""

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="items")
    # PROTECT to prevent deleting ticket types that are part of existing bookings
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # Price at the time of booking to ensure historical accuracy
    price_at_booking = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    class Meta:
        # A booking cannot have two booking items for the same ticket type
        unique_together = ("booking", "ticket_type")
        ordering = ["ticket_type__name"]

    def __str__(self):
        return f"{self.quantity} x {self.ticket_type.name} for Booking {self.booking.booking_reference}"
