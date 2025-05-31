# import factory
# from events.models import TicketType

# from .event_factory import EventFactory


# class TicketTypeFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = TicketType

#     event = factory.SubFactory(EventFactory)
#     name = factory.Sequence(lambda n: f"Ticket {n}")
#     description = "General Admission"
#     price = 55.50
#     quantity_available = 100
#     quantity_sold = 0
