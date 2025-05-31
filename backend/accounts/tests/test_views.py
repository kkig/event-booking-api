# Static analysis and IDE support
from typing import cast

import pytest
from accounts.models import User as CustomUser
from common.choices import UserRole
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()

REGISTER_URL = reverse("accounts:register")


# === Test User Registration ===
@pytest.mark.django_db
def test_user_registration_success(api_client):
    """
    Test that a new user can successfully register with valid data.
    """
    data = {
        "username": "newapiuser",
        "email": "newapiuser@example.com",
        "password": "Strong@Password123!",  # Password that passes validate_password
        "role": UserRole.ATTENDEE.value,
    }

    response = api_client.post(REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1

    _user_instance = User.objects.first()
    assert _user_instance is not None

    created_user = cast(CustomUser, _user_instance)
    assert created_user.username == "newapiuser"
    assert created_user.email == "newapiuser@example.com"
    assert created_user.check_password("Strong@Password123!")
    assert created_user.role == UserRole.ATTENDEE
    assert "id" in response.data


@pytest.mark.django_db
def test_user_registration_missing_required_fields(api_client):
    """
    Test registration with missing required fields (e.g., username, password)
    """
    data = {
        "email": "missing@example.com",
        "password": "StrongPassword123!",
        "role": UserRole.ATTENDEE.value,
        # 'username' is missing
    }

    response = api_client.post(REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "username" in response.data
    )  # Expect serializer validation errors for missing username
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_user_registration_invalid_password(api_client):
    """
    Tests registration with a password that fails Django's validate_password.
    """
    data = {
        "username": "weakpassuser",
        "email": "weak@example.com",
        "password": "123",  # Very weak password that should fail validate_password
        "role": UserRole.ATTENDEE.value,
    }

    response = api_client.post(REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data  # Expect password validation error
    assert "This password is too short" in str(response.data["password"])
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_user_registration_duplicate_username(api_client, user_factory):
    """
    Tests registration with an existing username.
    """
    existing_user = user_factory.create(
        username="existingapiuser"
    )  # Create a user with factory
    data = {
        "username": existing_user.username,  # Duplicate username
        "email": "another@example.com",
        "password": "NewPassword123!",
        "role": UserRole.ATTENDEE.value,
    }
    response = api_client.post(REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data  # Expect username validation error
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_user_registration_invalid_email(api_client):
    """
    Tests registration with an invalid email format.
    """
    data = {
        "username": "basemail",
        "email": "invalid-email",  # Invalid email format
        "password": "StrongPassword123!",
        "role": UserRole.ATTENDEE.value,
    }

    response = api_client.post(REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_user_registration_invalid_role(api_client):
    """
    Tests registration with an invalid role value.
    """
    data = {
        "username": "badroleuser",
        "email": "badrole@example.com",
        "password": "StrongPassword123!",
        "role": "super_admin",  # Invalid role
    }

    response = api_client.post(REGISTER_URL, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "role" in response.data
    assert User.objects.count() == 0
