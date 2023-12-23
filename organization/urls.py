from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSets

app_name = 'organization'

router = DefaultRouter()
router.register('', OrganizationViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
