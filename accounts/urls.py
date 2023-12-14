from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import routers

from . import views

app_name = "user"
router = routers.DefaultRouter()

router.register("", viewset=views.UserViewSets)


urlpatterns = [
    path("users/", include(router.urls)),
    path("signup/", views.UserSignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("verify-user-token/", views.VerifyAccountView.as_view(), name="verify_user_token"),
    path(
        "initiate-password-reset/",
        views.PasswordResetRequestView.as_view(),
        name="initiate_password_reset",
    ),
    path(
        "reset-password/",
        views.PasswordResetConfirmView.as_view(),
        name="reset_password",
    ),
    path("jwt/create/", TokenObtainPairView.as_view(), name="jwt_create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
