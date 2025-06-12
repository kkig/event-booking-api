from common.choices import EventStatus
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    name = models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255)
    total_capacity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=10, choices=EventStatus, default=EventStatus.UPCOMING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]  # Default ordering by date

    def __str__(self):
        return self.name

    @property
    def total_tickets_sold(self):
        try:
            return sum(tt.quantity_sold for tt in self.ticket_types.all())  # type: ignore[attr-defined]
        except Exception as e:
            print(f"Error fetching ticket_types: {e}")
            return 0


class TicketType(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="ticket_types",
    )
    name = models.CharField(max_length=100, validators=[MinLengthValidator(1)])
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity_available = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    quantity_sold = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "event",
                    "name",
                ),
                name="unique_ticket_type_name_per_event",
            )
        ]  # A event cannot have two ticket types with the same name
        ordering = ["price"]  # Default ordering by price

    def __str__(self):
        return f"{self.event.name} - {self.name}"
