from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TopicViewSets

app_name = 'topics'

router = DefaultRouter()
router.register('', TopicViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
