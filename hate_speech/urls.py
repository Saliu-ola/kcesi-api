from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BadWordsViewSets,SearchBadWordRelatedTermsView
app_name = 'hate-speech'

router = DefaultRouter()
router.register('', BadWordsViewSets)


urlpatterns = [
    path('search-bad-words/', SearchBadWordRelatedTermsView.as_view(), name='search-bad-words'),
    path('', include(router.urls)),
]
