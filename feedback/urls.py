from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSets

app_name = 'feedbacks'

router = DefaultRouter()

router.register('', FeedbackViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
