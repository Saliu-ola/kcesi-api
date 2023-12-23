from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSets

app_name = 'chat'

router = DefaultRouter()
router.register('', ChatViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
