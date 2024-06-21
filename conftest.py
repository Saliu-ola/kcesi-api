import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.tests.factories import UserFactory
from accounts.models import User
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication

AUTH_LOGIN_URL = reverse("user:login")


@pytest.fixture
def verified_admin_user():
    admin = UserFactory(
        is_verified=True,
        is_superuser=False,
        organization_name="ADMINISTRATION",
        role_id=2,
        group_id=22,
    )
    return admin


@pytest.fixture
def verified_super_user():
    super_user = UserFactory(
        is_verified=True,
        is_superuser=True,
        role_id=1,
    )
    return super_user


@pytest.fixture
def verified_user():
    user = UserFactory(
        is_verified=True,
        is_superuser=False,
        organization_name="ADMINISTRATION",
        role_id=2,
        group_id=22,
    )
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
def mocked_user_authentication(verified_user: User, mocker):
    def _user(is_verified=True, is_active=True, is_superuser=False):
        verified_user.is_active = is_active
        verified_user.is_verified = is_verified
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


@pytest.fixture
def mocked_admin_authentication(verified_admin_user: User, mocker):
    def _admin_user(is_verified=True, is_active=True, is_superuser=False):
        verified_admin_user.is_active = is_active
        verified_admin_user.is_verified = is_verified
        verified_admin_user.is_superuser = is_superuser
        verified_admin_user.save()
        verified_admin_user.refresh_from_db()
        mocked_user_data = {
            "email": verified_admin_user.email,
            "role": verified_admin_user.role_id,
            "organization_id": verified_admin_user.organization_id,
            "organization_name": verified_admin_user.organization_name,
        }
        mocker.patch.object(
            JWTAuthentication, "authenticate", return_value=(verified_admin_user, None)
        )
        return mocked_user_data

    return _admin_user


@pytest.fixture
def mocked_super_user_authentication(verified_super_user: User, mocker):
    def _super_user(is_verified=True, is_active=True, is_superuser=True):
        verified_super_user.is_active = is_active
        verified_super_user.is_verified = is_verified
        verified_super_user.is_superuser = is_superuser
        verified_super_user.save()
        verified_admin_user.refresh_from_db()
        mocked_user_data = {
            "email": verified_super_user.email,
            "role": verified_super_user.role_id,
        }
        mocker.patch.object(
            JWTAuthentication, "authenticate", return_value=(verified_admin_user, None)
        )
        return mocked_user_data

    return _super_user
