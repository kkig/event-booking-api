import django_filters
from common.choices import BookingStatus


class BookingFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at__lte = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    status = django_filters.ChoiceFilter(choices=BookingStatus.choices)
    event = django_filters.NumberFilter(field_name="event")

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data and "status" in data:
            data = data.copy()
            data["status"] = data["status"].lower()
            kwargs["data"] = data
        super().__init__(*args, **kwargs)
