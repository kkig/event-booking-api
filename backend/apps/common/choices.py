from django.db import models


class UserRole(models.TextChoices):
    ATTENDEE = "attendee", "Attendee"
    ORGANIZER = "organizer", "Organizer"


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"


class EventStatus(models.TextChoices):
    UPCOMING = "upcoming", "Upcoming"
    CANCELLED = "cancelled", "Cancelled"
    SOLD_OUT = "sold_out", "Sold Out"
    PAST = "past", "Past"
