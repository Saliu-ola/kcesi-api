 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSets

app_name = 'categroy'

router = DefaultRouter()

router.register('', CategoryViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
