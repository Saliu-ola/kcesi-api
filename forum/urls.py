from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForumViewSets

app_name = 'forum'

router = DefaultRouter()

router.register('', ForumViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
