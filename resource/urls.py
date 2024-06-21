from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourcesViewSets

app_name = 'resource'

router = DefaultRouter()
router.register('', ResourcesViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
