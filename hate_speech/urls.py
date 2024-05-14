from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BadWordsViewSets
app_name = 'hate-speech'

router = DefaultRouter()
router.register('', BadWordsViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
