import factory
from bookings.models import Booking, BookingItem
from common.choices import BookingStatus
from common.tests.factories import UserFactory
from events.tests.factories import EventFactory, TicketTypeFactory


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = BookingStatus.PENDING


class BookingItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookingItem

    booking = factory.SubFactory(BookingFactory)
    ticket_type = factory.SubFactory(TicketTypeFactory)
    quantity = factory.Faker("pyint", min_value=1, max_value=5)
