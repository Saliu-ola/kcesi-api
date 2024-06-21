import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import Token


login_url = reverse("user:login")

pytestmark = pytest.mark.django_db


class TestAuthEndpoints:
    def test_user_login(self, api_client, verified_user, auth_user_password):
        data = {"email": verified_user.email, "password": auth_user_password}
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_200_OK
        returned_json = response.json()

        assert "refresh" in returned_json["tokens"]
        assert "access" in returned_json["tokens"]

    def test_deny_login_for_unverified_user(self, api_client, unverified_user, auth_user_password):
        data = {"email": unverified_user.email, "password": auth_user_password}
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_deny_login_invalid_credentials(self, api_client, verified_user):
        data = {"email": verified_user.email, "password": "wrong@pass"}
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # def test_signup_regular_user(self):
    #     payload ={

    #     }

    #todo  test_verify user, password reset and initiate,
