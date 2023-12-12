import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.tests.factories import UserFactory
from accounts.models import User
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication

AUTH_LOGIN_URL = reverse("user:login")


@pytest.fixture
def verified_user():
    user = UserFactory(is_verified=True, is_superuser=False, is_staff=True)
    return user


@pytest.fixture
def unverified_user():
    user = UserFactory(is_verified=False, is_superuser=False, is_staff=True)
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_user_password() -> str:
    """returns user password to be used in authentication"""
    return "passer@@@111"


@pytest.fixture
def authenticate_user(api_client, verified_user: User, auth_user_password):
    """Creates a user and returns token needed for authentication"""
    payload = {"email": verified_user.email, "password": auth_user_password}

    response = api_client.post(AUTH_LOGIN_URL, data=payload)
    token = response.json()["access"]

    return {
        "token": token,
        "email": verified_user.email,
        "role": verified_user.role_id,
        "organization_id": verified_user.organization_id,
    }


@pytest.fixture
def mocked_authentication(verified_user: User, mocker):
    def _user(verified_user, is_active=True, is_superuser=False):
        verified_user.is_active = is_active
        verified_user.is_superuser = is_superuser
        verified_user.save()
        verified_user.refresh_from_db()
        mocked_user_data = {
            "email": verified_user.email,
            "role": verified_user.role_id,
            "organization_id": verified_user.organization_id,
            "organization_name": verified_user.organization_name,
        }
        mocker.patch.object(JWTAuthentication, "authenticate", return_value=(verified_user, None))
        return mocked_user_data

    return _user
