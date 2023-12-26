from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InAppChatViewSets

app_name = 'in_app_chat'

router = DefaultRouter()
router.register('', InAppChatViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
