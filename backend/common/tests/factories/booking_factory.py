import factory
from bookings.models import Booking
from common.choices import BookingStatus
from common.tests.factories import EventFactory, UserFactory


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = BookingStatus.PENDING
