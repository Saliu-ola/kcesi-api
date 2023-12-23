from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlatformViewSets

app_name = 'platform'

router = DefaultRouter()
router.register('', PlatformViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
