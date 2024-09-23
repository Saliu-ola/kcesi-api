from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'topics'

router = DefaultRouter()
# router.register('', TopicViewSets)
router.register(r'blog-topics', BlogTopicViewSet, basename='blog-topic')
router.register(r'forum-topics', ForumTopicViewSet, basename='forum-topic')


urlpatterns = [
    path('', include(router.urls)),
]
