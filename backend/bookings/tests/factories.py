from decimal import Decimal
from uuid import uuid4

from accounts.tests.factories import UserFactory
from bookings.models import Booking, BookingItem
from common.choices import BookingStatus
from events.tests.factories import EventFactory, TicketTypeFactory
from factory import (
    Faker,
    LazyFunction,
    SubFactory,
    django,
    lazy_attribute,
    post_generation,
)


# pyright: reportAttributeAccessIssue=false
class BookingFactory(django.DjangoModelFactory):
    class Meta:
        model = Booking
        skip_postgeneration_save = True  # Explicit opt-out of auto-save

    user = SubFactory(UserFactory)
    event = SubFactory(EventFactory)
    status = BookingStatus.CONFIRMED

    booking_reference = LazyFunction(uuid4)
    total_price = Decimal("0.00")  # Will be updated after items are added

    @post_generation
    def with_items(booking, create, extracted, **kwargs):
        """
        Optional: `BookingFactory(with_items=3)` create 3 BookingItems
        and updates total_price accordingly.
        """
        if not create or not extracted:
            return

        total = Decimal("0.00")
        for _ in range(extracted):
            item = BookingItemFactory(booking=booking, ticket_type__event=booking.event)
            total += item.price_at_booking * item.quantity

        booking.total_price = total
        booking.save()


class BookingItemFactory(django.DjangoModelFactory):
    class Meta:
        model = BookingItem
        skip_postgeneration_save = True  # Avoid future deprecation warning

    booking = SubFactory(BookingFactory)
    ticket_type = SubFactory(TicketTypeFactory)
    quantity = Faker("pyint", min_value=1, max_value=5)

    @lazy_attribute
    def price_at_booking(self):
        return self.ticket_type.price

    @post_generation
    def align_ticket_event(obj, create, extracted, **kwargs):
        if not create:
            return
        # Ensures ticket_type.event == booking.event for consistency
        if obj.ticket_type.event != obj.booking.event:
            obj.ticket_type.event = obj.booking.event
            obj.ticket_type.save()
