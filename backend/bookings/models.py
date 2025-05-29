from django.conf import settings
from django.db import models
from events.models import Event, TicketType


class Booking(models.Model):
    """User's reservation for an event."""

    class BookingStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.ACTIVE
    )

    def __str__(self):
        return f"Booking {self.event} for {self.user}"


class BookingItem(models.Model):
    """Specific ticket type and quantity for a booking."""

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="items")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.ticket_type.name} ({self.booking})"
