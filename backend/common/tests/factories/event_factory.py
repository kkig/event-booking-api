from datetime import timedelta

import factory
from common.choices import EventStatus
from common.tests.factories import UserFactory
from django.utils import timezone
from events.models import Event


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    organizer = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Test Event {n}")
    description = factory.Faker("paragraph")
    location = factory.Faker("city")
    start_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    end_time = factory.LazyAttribute(lambda obj: obj.start_time + timedelta(hours=2))
    capacity = 100
    status = EventStatus.UPCOMING
