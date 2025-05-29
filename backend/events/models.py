from common.choices import EventStatus
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10, choices=EventStatus, default=EventStatus.UPCOMING
    )
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # On creation, default quantity_sold to 0
        if not self.pk:
            self.quantity_sold = 0
        # Execute DB write
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.event.title}"
