from common.choices import BookingStatus
from django.contrib.auth import get_user_model
from django.db import models
from events.models import Event, TicketType

User = get_user_model()


class Booking(models.Model):
    """User's reservation for an event."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.event} for {self.user}"


class BookingItem(models.Model):
    """Specific ticket type and quantity for a booking."""

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="items")
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.ticket_type.name} for {self.booking}"
