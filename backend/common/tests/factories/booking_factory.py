import factory
from bookings.models import Booking
from common.choices import BookingStatus

from .event_factory import EventFactory
from .user_factory import UserFactory


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = BookingStatus.PENDING
