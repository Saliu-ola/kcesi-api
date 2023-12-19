from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSets

app_name = 'group'

router = DefaultRouter()
router.register('', GroupViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
