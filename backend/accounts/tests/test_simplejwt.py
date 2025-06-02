# Static analysis and IDE support
from typing import cast

import pytest
from accounts.models import User as MyUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

LOGIN_URL = reverse("accounts:token_obtain_pair")


# === Tests for JWT Authentication (Login) === #
def test_jwt_login_missing_fields(api_client):
    """
    Test request without required data should return 400.
    """
    data = {}
    response = api_client.post(LOGIN_URL, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data
    assert "password" in response.data


def test_jwt_login_missing_username(api_client):
    """
    Test request without username.
    """
    data = {"password": "AnyPassword"}
    response = api_client.post(LOGIN_URL, data, json="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data  # Expect serializer validation error


def test_jwt_login_missing_password(api_client):
    """
    Test request without password.
    """
    data = {"username": "AnyPassword"}
    response = api_client.post(LOGIN_URL, data, json="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data


@pytest.mark.django_db
def test_jwt_organizer_login_success(api_client, organizer_factory):
    """
    Tests successful JWT token obtainment with valid credentials for organizers.
    """
    # Use a distict val for clarity
    password = "TestPassword123!"

    # Factory generate the username and other default fields.
    user: MyUser = cast(MyUser, organizer_factory.create())

    # Explicitly set the password for this user instance
    # Use Django's method to hash it
    user.set_password(password)

    # You must save after set_password()
    user.save()

    # Confirm user created and active
    assert User.objects.count() == 1

    # Fetch the user explicitly from the database by its ID
    organizer_user: MyUser = cast(MyUser, User.objects.get(pk=user.pk))
    assert organizer_user is not None

    username = organizer_user.username

    # Login User
    data = {"username": username, "password": password}
    response = api_client.post(LOGIN_URL, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

    # Verify the access token structure
    access_toke = AccessToken(response.data["access"])
    assert str(access_toke.payload["user_id"]) == str(user.pk)


@pytest.mark.django_db
def test_jwt_attendee_login_success(api_client, attendee_factory):
    """
    Tests successful JWT token obtainment with valid credentials for attendees.
    """
    # Use a distict val for clarity
    password = "TestPassword123!"

    # Factory generate the username and other default fields.
    user: MyUser = cast(MyUser, attendee_factory.create())

    # Explicitly set the password for this user instance
    # Use Django's method to hash it
    user.set_password(password)
    user.save()

    assert User.objects.count() == 1

    attendee_user: MyUser = cast(MyUser, User.objects.get(pk=user.pk))
    assert attendee_user is not None

    # Login User
    data = {"username": attendee_user.username, "password": password}
    response = api_client.post(LOGIN_URL, data, format="json")

    # Verify response
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

    # Verify the access token structure
    access_token = AccessToken(response.data["access"])
    assert str(access_token.payload["user_id"]) == str(user.pk)


@pytest.mark.django_db
def test_jwt_login_invalid_credentials_username(api_client, user_factory):
    """
    Tests JWT token obtainment with an invalid username.
    """
    # Create new user - explicitly set password that will be hashed
    password = "CorrectPassword123!"
    new_user = cast(MyUser, user_factory.build(username="nonexistentuser"))
    new_user.set_password(password)
    new_user.save()

    # Try Login
    data = {"username": "anyusername", "password": password}
    response = api_client.post(LOGIN_URL, data, format="json")

    # Verify response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert (
        response.data["detail"] == "No active account found with the given credentials"
    )


@pytest.mark.django_db
def test_jwt_login_invalid_credentials_password(api_client, user_factory):
    """
    Tests JWT token obtainment with an invalid password.
    """
    # Create new user
    username = "nonexistentuser"
    new_user = user_factory.build(username=username)
    new_user.set_password("CorrectPassword123!")

    # Try Login
    data = {"username": username, "password": "IncorrectPassword!"}
    response = api_client.post(LOGIN_URL, data, format="json")

    # Verify response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert (
        response.data["detail"] == "No active account found with the given credentials"
    )
