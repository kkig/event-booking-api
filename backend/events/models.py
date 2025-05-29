from django.conf import settings
from django.db import models


class Event(models.Model):
    STATUS_CHOICES = (
        ("upcoming", "Upcoming"),
        ("cancelled", "Cancelled"),
        ("sold_out", "Sold Out"),
        ("past", "Past"),
    )

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="upcoming")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TicketType(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="ticket_types",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    quantity_available = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # On creation, default quantity_available to quantity
        if not self.pk:
            self.quantity_available = self.quantity
        # Execute DB write
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.event.title}"
