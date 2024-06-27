from django.urls import path
from .views import FlagCreateView, CheckFlagStatus,ActivityFlagListView, ActivityFlagDeleteView, ActivityFlagRetrieveView
# from .views import FlagActivityView

urlpatterns = [
    path('create-flags/', FlagCreateView.as_view(), name='create-flag'),
    path('check-status/', CheckFlagStatus.as_view(), name='check-flag'), #Test Purposes

    # path('retrieve-delete/<int:group_id>/<int:activity_type_id>/<int:activity_id>/', ActivityFlagRetrieveDeleteView.as_view(), name='activity-flag-detail'),
    path('list-flags/', ActivityFlagListView.as_view(), name='list-flag'),
    path('retrieve/<int:id>/', ActivityFlagRetrieveView.as_view(), name='activity-flag-detail'),
    path('delete/<int:id>/', ActivityFlagDeleteView.as_view(), name='activity-flag-delete'),
    # path('create-flags/', FlagActivityView.as_view(), name='flag-activity'),


]
