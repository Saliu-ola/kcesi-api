from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrowserHistoryViewSets

app_name = 'browser_histroy'

router = DefaultRouter()

router.register('', BrowserHistoryViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
