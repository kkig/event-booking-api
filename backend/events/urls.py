from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import EventViewSet, TicketTypeViewSet

# Router instance that generates url partterns
# (e.g. GET /, GET /<id>)
router = DefaultRouter()

# Main router for events - /api/events/ prefix defined in project urls.py
router.register("", EventViewSet, basename="event")

# Nested router for ticket-types under events - /events/{lookup}_pk/ticket-types/
event_router = NestedDefaultRouter(router, "", lookup="event")
event_router.register(r"ticket-types", TicketTypeViewSet, basename="event-ticket-types")

# Final URL patterns
urlpatterns = router.urls + event_router.urls
