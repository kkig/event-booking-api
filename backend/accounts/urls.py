from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    # Authenticate and return access + refresh token pair - token based auth
    path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Sends refresh token and get access token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
