from typing import cast

import pytest
from accounts.constants import AccountsMessages
from accounts.models import User as MyUser
from accounts.tests.test_simplejwt import LOGIN_URL
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()

DEACTIVATE_URL = reverse("accounts:deactivate_account")
USER_PROFILE_URL = reverse("accounts:user_profile")


@pytest.mark.django_db
def test_deactivate_account_success(api_client, organizer_factory):
    """
    Tests an authenticated user can successfully deactivate their account.
    """
    password = "MySecurePassword123!"
    user: MyUser = cast(
        MyUser,
        organizer_factory.create(
            email="deactivate_user@example.com",
            is_active=True,
        ),
    )
    user.set_password(password)
    user.save()

    # Log in the user
    login_data = {"username": user.username, "password": password}
    login_response = api_client.post(LOGIN_URL, login_data, format="json")
    access_token = login_response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # Deactivate the account
    response = api_client.delete(DEACTIVATE_URL)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert AccountsMessages.DEACTIVATED in response.data["detail"]

    # Verify user's is_activae status in the database
    user.refresh_from_db()
    assert not user.is_active

    # Try to log in with the deactivated account (should fail)
    api_client.credentials()  # Clear current token
    login_fail_response = api_client.post(LOGIN_URL, login_data, format="json")
    assert login_fail_response.status_code == status.HTTP_401_UNAUTHORIZED

    # Try to access profile with deactivated account (Shoud fail or result in 401 with old token)
    # Re-set credentials with the old token, which should now be invalid because user is inactive
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    profile_response = api_client.get(USER_PROFILE_URL)

    # Token becomes invalid for inactive user
    assert profile_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_deactivate_account_unauthenticated(api_client):
    """
    Test an unauthenticated user cannot deactivate an account.
    """
    response = api_client.delete(DEACTIVATE_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_deactivate_already_inactive_account(api_client, organizer_factory, mocker):
    """
    Tests that attempting to deactivate an aleady inactive account returns a 400.
    """
    user_email = "already_inactive@example.com"
    password = "AnotherSecurePassword123!"
    inactive_user: MyUser = cast(
        MyUser,
        organizer_factory.build(
            email=user_email,
            is_active=False,  # Start as inactive
        ),
    )
    inactive_user.set_password(password)
    inactive_user.save()

    # To satisfy `permissions.IsAuthenticated`, we need a valid token.
    # We'll create a token for a *separate, active* dummy user.
    active_dummy_user: MyUser = cast(
        MyUser,
        organizer_factory.build(
            email="active_dummy_for_mock@example.com",
            password="ActiveDummyPassword123!",
            is_active=True,
        ),
    )
    active_dummy_user.set_password("ActiveDummyPassword123!")
    active_dummy_user.save()

    login_response = api_client.post(
        LOGIN_URL,
        {"username": active_dummy_user.username, "password": "ActiveDummyPassword123!"},
        format="json",
    )
    access_token = login_response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # We use mocker.patch to replace `request.user` with our `inactive_user` object
    # for the duration of this specific test request.
    # This makes the `IsAuthenticated` permission pass (due to the valid token),
    # but when the `delete` method runs, `request.user` will be the `inactive_user`.
    mocker.patch(
        "rest_framework.request.Request.user",
        new_callable=mocker.PropertyMock(return_value=inactive_user),
    )

    # Attempt to deactivate the account
    print(f"DEBUG: Attempting to deactivate URL: {DEACTIVATE_URL}")
    response = api_client.delete(DEACTIVATE_URL)
    print(f"DEBUG: Response status: {response.status_code}, data: {response.data}")

    # Assert the expected 400 response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == AccountsMessages.ALREADY_INACTIVE

    # Verify the user remain inactive in the database
    inactive_user.refresh_from_db()
    assert not inactive_user.is_active
