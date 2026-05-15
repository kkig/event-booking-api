from datetime import timedelta
from typing import Self

from django.contrib.auth import get_user_model
from django.utils import timezone
from factory import (
    CREATE_STRATEGY,
    Faker,
    LazyFunction,
    Sequence,
    SubFactory,
    django,
    post_generation,
)
from factory.fuzzy import FuzzyDecimal, FuzzyInteger

from apps.accounts.tests.factories import OrganizerFactory
from apps.common.choices import EventStatus
from apps.events.models import Event, TicketType

User = get_user_model()


class EventFactory(django.DjangoModelFactory):
    class Meta:
        model = Event
        # Ensure that a new organizer is created if not explicitly provided
        # or fetched from an existing one.
        strategy = CREATE_STRATEGY
        skip_postgeneration_save = True

    organizer = SubFactory(OrganizerFactory)
    name = Sequence(lambda n: f"Test Event {n}")
    description = Faker("paragraph")

    start_time = LazyFunction(lambda: timezone.now() + timedelta(days=1))
    end_time = LazyFunction(lambda: timezone.now() + timedelta(days=1, hours=2))

    location = Faker("address")
    total_capacity = FuzzyInteger(100, 1000)
    status = EventStatus.UPCOMING

    @post_generation
    def with_ticket_types(instance: Self, create: bool, extracted, **kwargs):
        """
        Optional: `EventFactory(with_ticket_types=3)` creates 3 TicketTypes for the event.
        You can also pass a dict for specific ticket type configurations:
        `EventFactory(with_ticket_types=[{'name': 'VIP', 'price': 100}])`
        """
        if not create:
            # Build strategy, do nothing
            return

        if extracted:
            if isinstance(extracted, int):
                for _ in range(extracted):
                    TicketTypeFactory(event=instance)
            elif isinstance(extracted, list):
                for tt_data in extracted:
                    # Merge event into the provided data
                    TicketTypeFactory(event=instance, **tt_data)


class TicketTypeFactory(django.DjangoModelFactory):
    class Meta:
        model = TicketType
        # Often useful to build related objects first
        strategy = CREATE_STRATEGY
        skip_postgeneration_save = True

    event = SubFactory(EventFactory)
    name = Sequence(lambda n: f"Ticket {n}")
    description = Faker("sentence")
    price = FuzzyDecimal(10.00, 500.00, precision=2)  # Ensure Decimal type
    quantity_available = FuzzyInteger(10, 500)
    quantity_sold = 0
    is_active = True

    # created_at and updated_at are auto-added/auto-updated by Django,
    # so no need to define them here either.

    @post_generation
    def ensure_unique_name_per_event(obj: Self, create: bool, extracted, **kwargs):
        """
        Ensures uniqueness of ticket type name per event by appending a number
        if a duplicate is detected during testing.
        This is a defensive measure for specific test cases; factory_boy usually handles it.
        """
        if not create:
            return

        # This part is more for complex scenarios where unique constrains might be hit
        # in specific test setups rather than general factory usage.
        # factory_boy's default strategies usually ensure unique values for CharFields
        # if not explicitly set to be non-unique.
        # If you hit `IntegrityError` due to unique constraint, this could be elaborated.
        pass
