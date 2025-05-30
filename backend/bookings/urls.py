from bookings.views.update import BookingCancelView
from django.urls import path

from .views import BookingCreateView, BookingDetailView, BookingListView

url_prefix = "bookings/"

urlpatterns = [
    path("users/me/bookings", BookingListView.as_view(), name="my-bookings"),
    path(f"{url_prefix}<int:pk>", BookingDetailView.as_view(), name="booking-detail"),
    path(f"{url_prefix}", BookingCreateView.as_view(), name="booking-create"),
    path(
        f"{url_prefix}<int:pk>/cancel",
        BookingCancelView.as_view(),
        name="booking-cancel",
    ),
]
