from typing import cast

import pytest
from accounts.constants import (
    PASSWORD_RESET_CONFIRM_NAME,
    PasswordMessasges,
)
from accounts.models import User as MyUser
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status

User = get_user_model()

LOGIN_URL = reverse("accounts:token_obtain_pair")
PASSWORD_RESET_REQUEST_URL = reverse("accounts:password_reset_request")
# Note: PASSWORD_RESET_CONFIRM_URL will be built dynamically in tests


# === Helper function to get UID and Token ===
def get_uid_and_token_from_email(user: MyUser):
    # Ensure there's an email in the outbox
    assert len(mail.outbox) >= 1
    # Assuming the latest email is the reset email
    email_body = mail.outbox[-1].body

    # Extract UID and token from the email body's reset link
    # This regex looks for patterns like /password-reset-confirm/base64uid/token/
    import re

    url = r"password-reset-confirm/([0-9A-Za-z_\-]+)/([0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/"

    match = re.search(
        url,
        email_body,
    )
    assert match is not None, "Could not find reset link in email body"
    uid = match.group(1)
    token = match.group(2)
    return uid, token


# === Tests for Password Reset Confirmation ===
@pytest.mark.django_db
def test_password_reset_confirm_success(api_client, organizer_factory):
    """
    Tests that a password can be successfully reset using a valid UID and token.
    """
    user_email = "confirm_success@example.com"
    old_password = "OldPass123!"
    new_password = "NewResetPassword456!"

    user: MyUser = cast(MyUser, organizer_factory.create(email=user_email))
    user.set_password(old_password)
    user.save()

    # Request password reset email
    mail.outbox = []
    api_client.post(PASSWORD_RESET_REQUEST_URL, {"email": user_email}, format="json")
    assert len(mail.outbox) == 1

    # Extract UID and Token from the sent email
    uid, token = get_uid_and_token_from_email(user)

    # Construct the correct URL for the confirmation endpoint
    # Pass the uid and token as keyword arguments
    reset_confirm_url = reverse(
        PASSWORD_RESET_CONFIRM_NAME, kwargs={"uidb64": uid, "token": token}
    )

    # Prepare data for confirmation
    confirm_data = {
        "uid": uid,
        "token": token,
        "new_password1": new_password,
        "new_password2": new_password,
    }

    # Post to the password reset confirm endpoint
    response = api_client.post(
        reset_confirm_url,
        confirm_data,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["detail"] == "Password has been reset successfully."

    # Verify old password no longer works and new one does
    api_client.credentials()  # Clear credentials
    login_fail_response = api_client.post(
        LOGIN_URL, {"username": user.username, "password": old_password}, format="json"
    )
    assert login_fail_response.status_code == status.HTTP_401_UNAUTHORIZED

    login_success_response = api_client.post(
        LOGIN_URL, {"username": user.username, "password": new_password}, format="json"
    )
    assert login_success_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_password_reset_confirm_invalid_uid(api_client):
    """
    Tests password reset confirmation fails with an invalid UID.
    """
    reset_confirm_url = reverse(
        PASSWORD_RESET_CONFIRM_NAME,
        kwargs={"uidb64": "invalid-uid", "token": "valid-token"},
    )

    confirm_data = {
        "uid": "invalid-uid",  # Invalid UID
        "token": "valid-token",
        "new_password1": "NewPass123!",
        "new_password2": "NewPass123!",
    }
    response = api_client.post(reset_confirm_url, confirm_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "uid" in response.data
    assert PasswordMessasges.INVALID_UID_OR_NO_USER in response.data["uid"][0]


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(api_client, organizer_factory):
    """
    Tests password reset confirmation fails with an invalid token.
    """
    user_email = "confirm_invalid_token@example.com"
    user: MyUser = cast(MyUser, organizer_factory.create(email=user_email))

    # Request password reset email to get a valid UID
    mail.outbox = []
    api_client.post(PASSWORD_RESET_REQUEST_URL, {"email": user_email}, format="json")
    assert len(mail.outbox) == 1

    uid, _ = get_uid_and_token_from_email(user)  # Only need UID
    invalid_token = "abc-defg"

    reset_confirm_url = reverse(
        PASSWORD_RESET_CONFIRM_NAME,
        kwargs={"uidb64": uid, "token": invalid_token},
    )
    confirm_data = {
        "uid": uid,
        "token": invalid_token,
        "new_password1": "NewPass123!",
        "new_password2": "NewPass123!",
    }

    response = api_client.post(reset_confirm_url, confirm_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data
    assert PasswordMessasges.RESET_LINK_EXPIRED in response.data["token"][0]


@pytest.mark.django_db
def test_password_reset_confirm_mismatched_new_passwords(api_client, organizer_factory):
    """
    Tests password reset confirmation fails if new passwords do not match.
    """
    user_email = "confirm_mismatch_pass@example.com"
    user: MyUser = cast(MyUser, organizer_factory.create(email=user_email))

    mail.outbox = []
    api_client.post(PASSWORD_RESET_REQUEST_URL, {"email": user_email}, format="json")
    uid, token = get_uid_and_token_from_email(user)

    reset_password_url = reverse(
        PASSWORD_RESET_CONFIRM_NAME, kwargs={"uidb64": uid, "token": token}
    )
    confirm_data = {
        "uid": uid,
        "token": token,
        "new_password1": "NewPass123!",
        "new_password2": "DifferentPass456!",  # Mismatched
    }
    response = api_client.post(reset_password_url, confirm_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "new_password2" in response.data
    assert PasswordMessasges.NOT_MATCH in response.data["new_password2"][0]


@pytest.mark.django_db
def test_password_reset_confirm_invalid_new_password_strength(
    api_client, organizer_factory
):
    """
    Tests password reset confirmation fails if new password does not meet strengthrequirements.
    """
    user_email = "confirm_weak_pass@example.com"
    user: MyUser = cast(MyUser, organizer_factory.create(email=user_email))

    mail.outbox = []
    api_client.post(PASSWORD_RESET_REQUEST_URL, {"email": user_email}, format="json")
    uid, token = get_uid_and_token_from_email(user)

    reset_password_url = reverse(
        PASSWORD_RESET_CONFIRM_NAME, kwargs={"uidb64": uid, "token": token}
    )
    confirm_data = {
        "uid": uid,
        "token": token,
        "new_password1": "123",  # Too weak
        "new_password2": "123",
    }
    response = api_client.post(reset_password_url, confirm_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "new_password1" in response.data
    assert "This password is too short." in response.data["new_password1"][0]


@pytest.mark.django_db
def test_password_reset_confirm_token_used_twice(api_client, organizer_factory):
    """
    Tests that a password reset token cannot be used more than once.
    """
    user_email = "confirm_twice@example.com"
    old_password = "OldPassToReset!"
    first_new_password = "FirstNewPass123!"
    second_new_password = "SecondNewPass456!"

    user: MyUser = cast(MyUser, organizer_factory.create(email=user_email))
    user.set_password(old_password)
    user.save()

    # Request password reset email
    mail.outbox = []
    api_client.post(PASSWORD_RESET_REQUEST_URL, {"email": user_email}, format="json")
    uid, token = get_uid_and_token_from_email(user)

    # Use the token successfully the first time
    reset_password_url_first = reverse(
        PASSWORD_RESET_CONFIRM_NAME, kwargs={"uidb64": uid, "token": token}
    )
    confirm_data_first = {
        "uid": uid,
        "token": token,
        "new_password1": first_new_password,
        "new_password2": first_new_password,
    }
    response_first = api_client.post(
        reset_password_url_first, confirm_data_first, format="json"
    )
    assert response_first.status_code == status.HTTP_200_OK

    # Try to use the same token again
    reset_password_url_second = reverse(
        PASSWORD_RESET_CONFIRM_NAME, kwargs={"uidb64": uid, "token": token}
    )
    confirm_data_second = {
        "uid": uid,
        "token": token,
        "new_password1": second_new_password,
        "new_password2": second_new_password,
    }
    response_second = api_client.post(
        reset_password_url_second, confirm_data_second, format="json"
    )

    assert response_second.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response_second.data
    assert PasswordMessasges.RESET_LINK_EXPIRED in response_second.data["token"][0]

    # Verify the user's password is the first new one, not the second
    api_client.credentials()
    login_fail_response_old = api_client.post(
        LOGIN_URL, {"username": user.username, "password": old_password}
    )
    assert login_fail_response_old.status_code == status.HTTP_401_UNAUTHORIZED

    login_success_response_first = api_client.post(
        LOGIN_URL, {"username": user.username, "password": first_new_password}
    )
    assert login_success_response_first.status_code == status.HTTP_200_OK

    login_fail_response_second = api_client.post(
        LOGIN_URL,
        {"username": user.username, "password": second_new_password},
        format="json",
    )
    assert login_fail_response_second.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_password_reset_confirm_token_expired(api_client, organizer_factory):
    """
    Tests that an expired password reset token cannot be used.
    Nole: This test relies on manipulating the token generator's lifetime.
    For a real test, use a custom token generator or mock time.
    """
    pass
