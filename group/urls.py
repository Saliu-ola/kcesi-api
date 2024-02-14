from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSets, UserGroupsViewSets

app_name = 'group'

router = DefaultRouter()
router.register('user-groups', UserGroupsViewSets)
router.register('', GroupViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
