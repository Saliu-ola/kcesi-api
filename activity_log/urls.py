from django.urls import path
from .views import ActivityLogListCreateView, ActivityLogRetrieveUpdateDestroyView

urlpatterns = [
    path('activity-logs/', ActivityLogListCreateView.as_view(), name='activity-log-list-create'),
    path('activity-logs/<int:pk>/', ActivityLogRetrieveUpdateDestroyView.as_view(), name='activity-log-detail'),
]