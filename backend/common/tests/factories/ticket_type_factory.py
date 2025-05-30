import factory
from common.tests.factories import EventFactory
from events.models import TicketType


class TicketTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketType

    event = factory.SubFactory(EventFactory)
    name = factory.Sequence(lambda n: f"Ticket {n}")
    description = "General Admission"
    price = 55.50
    quantity_available = 100
    quantity_sold = 0
