from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourcesTypeViewSets, ResourcesViewSets

app_name = 'resources'

router = DefaultRouter()
router.register('types', ResourcesTypeViewSets)
router.register('', ResourcesViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
