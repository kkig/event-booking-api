# Static analysis and IDE support
from typing import cast

import pytest
from accounts.models import User as MyUser
from common.choices import UserRole
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

LOGIN_URL = reverse("accounts:token_obtain_pair")
REFRESH_TOKEN_URL = reverse("accounts:token_refresh")
USER_PROFILE_URL = reverse("accounts:user_profile")


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


# === Tests for JWT Token Refresh ===
@pytest.mark.django_db
def test_jwt_token_refresh_success(api_client, organizer_factory):
    """
    Tests successful refresh of an access token using a valid refresh token.
    """
    password = "RefreshTestPassword123!"

    # Log in
    new_user: MyUser = cast(MyUser, organizer_factory.create())
    new_user.set_password(password)
    new_user.save()

    user: MyUser = cast(MyUser, User.objects.get(pk=new_user.pk))

    data = {"username": user.username, "password": password}
    response = api_client.post(LOGIN_URL, data, format="json")

    # Verify response
    assert response.status_code == status.HTTP_200_OK

    # Get refresh token and access token
    refresh_token = response.data["refresh"]
    initial_access_token = response.data["access"]

    # Use the refresh token to get a new access token
    refresh_data = {"refresh": refresh_token}
    refresh_response = api_client.post(REFRESH_TOKEN_URL, refresh_data, format="json")

    assert refresh_response.status_code == status.HTTP_200_OK
    assert "access" in refresh_response.data
    assert refresh_response.data["access"] != initial_access_token

    # Verify the new access token's integrity/claims
    new_access_token = AccessToken(refresh_response.data["access"])
    assert str(new_access_token.payload["user_id"]) == str(user.pk)


def test_jwt_token_refresh_invalid_token(api_client):
    """
    Tests refresh token endpoint with an invalid (malformed) refresh token.
    """
    data = {"refresh": "this.is.not.a.valid.jwt.token"}
    response = api_client.post(REFRESH_TOKEN_URL, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert response.data["detail"] == "Token is invalid"


def test_jwt_token_refresh_missing_token(api_client):
    """
    Tests refresh token endpoint with a missing refresh token.
    """
    data = {}
    response = api_client.post(REFRESH_TOKEN_URL, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "refresh" in response.data  # Expect serializer validation error
    assert "This field is required." in response.data["refresh"]


# === Tests for User Profile Management ===
@pytest.mark.django_db
def test_user_profile_retrieve_authenticated(api_client, organizer_factory):
    """
    Tests authenticated user can retrieve their own profile data.
    """
    password = "ProfileTestPassword123!"
    new_user: MyUser = cast(MyUser, organizer_factory.create(email="test@example.com"))
    new_user.set_password(password)
    new_user.save()

    user: MyUser = cast(MyUser, User.objects.get(pk=new_user.pk))

    # Authenticate the client
    data = {"username": user.username, "password": password}
    login_response = api_client.post(LOGIN_URL, data, format="json")
    access_token = login_response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # Send GET request to profile endpoint
    response = api_client.get(USER_PROFILE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.pk
    assert response.data["username"] == user.username
    assert response.data["email"] == "test@example.com"
    assert response.data["role"] == UserRole.ORGANIZER.value


def test_user_profile_retrieve_unauthenticated(api_client):
    """
    Tests unauthenticated user cannot retrieve profile data.
    """
    response = api_client.get(USER_PROFILE_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_profile_update_authenticated(api_client, organizer_factory):
    """
    Tests authenticated user can update their own profile data.
    """
    password = "UpdateTestPassword123!"
    new_user: MyUser = cast(MyUser, organizer_factory.build(email="old@example.com"))
    new_user.set_password(password)
    new_user.save()
    user: MyUser = cast(MyUser, User.objects.get(pk=new_user.pk))

    # Authenticate the client
    login_data = {"username": user.username, "password": password}
    login_response = api_client.post(LOGIN_URL, login_data, format="json")
    access_token = login_response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # Data to update
    update_data = {
        "email": "new@example.com",
    }

    # Send PUT/PATCH request to profile endpoint - PATCH for partial update
    response = api_client.patch(USER_PROFILE_URL, update_data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == "new@example.com"

    # Verify data actually changed in the database
    updated_user: MyUser = cast(MyUser, User.objects.get(pk=user.pk))
    assert updated_user.email == "new@example.com"
    assert updated_user.username == user.username


def test_user_profile_update_unauthenticated(api_client):
    """
    Test unauthenticated user cannot update profile data.
    """
    data = {"email": "hacker@example.com"}
    response = api_client.patch(USER_PROFILE_URL, data, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_profile_update_read_only_fields(api_client, organizer_factory):
    """
    Tests user cannot update read-only fields (like ID or role).
    """
    password = "ReadOnlyTestPassword123!"
    new_user: MyUser = cast(
        MyUser,
        organizer_factory.build(
            email="read_only@example.com", role=UserRole.ORGANIZER.value
        ),
    )
    new_user.set_password(password)
    new_user.save()

    db_user: MyUser = cast(MyUser, User.objects.get(pk=new_user.pk))

    # Authenticate the client
    login_data = {"username": db_user.username, "password": password}
    login_response = api_client.post(LOGIN_URL, login_data, format="json")
    access_token = login_response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # Attempt to update read-only fields
    bad_update_data = {
        "id": 9999,  # Trying to change ID
        "role": UserRole.ATTENDEE.value,  # Trying to change role
    }

    response = api_client.patch(USER_PROFILE_URL, bad_update_data, format="json")

    # Expect 200 OK because DRF by default ignores read-only fields on update.
    # The key is to assert that the values in the DB did NOT change.
    assert response.status_code == status.HTTP_200_OK

    # Verify data did NOT change in the database
    updated_db_user: MyUser = cast(MyUser, User.objects.get(pk=db_user.pk))
    assert updated_db_user.pk == db_user.pk
    assert updated_db_user.role == UserRole.ORGANIZER.value
