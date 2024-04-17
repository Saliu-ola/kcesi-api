from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogViewSets, CommentViewSets,ReplyViewSets

app_name = 'blog'

router = DefaultRouter()
router.register('comments', CommentViewSets)
router.register('comment-replies', ReplyViewSets)
router.register('', BlogViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
