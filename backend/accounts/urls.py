from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ChangePasswordView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    UserDeactivateView,
    UserProfileView,
)

app_name = "accounts"
reset_url_pattern = (
    r"(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$"
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    # Authenticate and return access + refresh token pair - token based auth
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Sends refresh token and get access token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "password-reset-request/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    # re_path is used to capture uid and token parts with slashes
    re_path(
        rf"password-reset-confirm/{reset_url_pattern}",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "deactivate-account/", UserDeactivateView.as_view(), name="deactivate_account"
    ),
]
