import factory
from bookings.models import BookingItem
from common.tests.factories import BookingFactory, TicketTypeFactory


class BookingItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookingItem

    booking = factory.SubFactory(BookingFactory)
    ticket_type = factory.SubFactory(TicketTypeFactory)
    quantity = 2
