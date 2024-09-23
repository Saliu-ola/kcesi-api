from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogViewSets, CommentViewSets,ReplyViewSets, BlogReadViewSet

app_name = 'blog'

router = DefaultRouter()
router.register('comments', CommentViewSets)
router.register('comment-replies', ReplyViewSets)
router.register(r'blog-reads', BlogReadViewSet, basename='blog-read')
router.register('', BlogViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
