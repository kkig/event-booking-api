import django_filters
from common.choices import BookingStatus

from .models import Booking


class BookingFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at__lte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    status = django_filters.ChoiceFilter(choices=BookingStatus.choices)

    class Meta:
        model = Booking
        fields = {
            "status": ["exact"],
            "event": ["exact"],
        }
