from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForumViewSets,CommentViewSets,ReplyViewSets

app_name = 'forum'

router = DefaultRouter()
router.register('comments', CommentViewSets)
router.register('comment-replies', ReplyViewSets)
router.register('', ForumViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
