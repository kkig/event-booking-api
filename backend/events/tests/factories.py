from datetime import timedelta

import factory
from accounts.tests.factories import OrganizerFactory
from common.choices import EventStatus
from django.contrib.auth import get_user_model
from django.utils import timezone
from events.models import Event, TicketType

User = get_user_model()


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    organizer = factory.SubFactory(OrganizerFactory)
    name = factory.Sequence(lambda n: f"Test Event {n}")
    description = factory.Faker("paragraph")
    location = factory.Faker("city")
    start_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    end_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1, hours=2))
    total_capacity = 100
    status = EventStatus.UPCOMING


class TicketTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketType

    event = factory.SubFactory(EventFactory)
    name = factory.Sequence(lambda n: f"Ticket {n}")
    description = "General Admission"
    price = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, min_value=10, max_value=200
    )
    quantity_available = factory.Faker("pyint", min_value=10, max_value=100)
    quantity_sold = 0
    is_active = True
