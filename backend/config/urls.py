"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_prefix = "api/"

urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI schema (JSON)
    path(f"{api_prefix}schema", SpectacularAPIView.as_view(), name="schema"),
    # Interactive Docs (Swagger / Redoc)
    path(
        f"{api_prefix}docs/swagger",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        f"{api_prefix}docs/redoc",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # Include your app routes here
    path(f"{api_prefix}auth/", include("accounts.urls")),
    path(f"{api_prefix}events/", include("events.urls")),
    path(f"{api_prefix}", include("bookings.urls")),
]
