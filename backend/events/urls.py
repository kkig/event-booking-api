from rest_framework.routers import DefaultRouter

from .views import EventViewSet

# Router instance that generates url partterns
# (e.g. GET /, GET /<id>)
router = DefaultRouter()

# .register(__prefix__, __viewset__, __name__)
router.register("", EventViewSet, basename="event")

urlpatterns = router.urls
