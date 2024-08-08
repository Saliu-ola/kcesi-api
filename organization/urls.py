from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSets, UserListByOrganization

app_name = "organization"

router = DefaultRouter()
router.register("", OrganizationViewSets)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "users-in-organization/<str:organization_id>/",
        UserListByOrganization.as_view(),
        name="users-by-organization",
    ),
]
