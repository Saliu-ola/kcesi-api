from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'group'

router = DefaultRouter()
router.register('user-groups', UserGroupsViewSets)
router.register('', GroupViewSets)



urlpatterns = [
    path('', include(router.urls)),
    path('get-user-in-group/<int:group_id>/', UsersInGroupView.as_view(), name = 'view-users-in-a-group'),
    
    
]
