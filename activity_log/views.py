from django.shortcuts import render
from .serializers import ActivityLogSerializer
from .models import ActivityLog
from accounts.permissions import IsSuperAdmin
from rest_framework import generics
# Create your views here.



class ActivityLogListCreateView(generics.ListCreateAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        # user = self.request.user if self.request.user.is_authenticated else None
        instance = serializer.save(action_user=self.request.user)


class ActivityLogRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsSuperAdmin]

    def perform_update(self, serializer):
        instance = serializer.save()
        
        # Log the update of an ActivityLog
        ActivityLog.objects.create(
            user=instance.user,
            action_user=self.request.user,
            action='update',
            object_id=instance.id,
            content_type='Activity-Log',
        )

    def perform_destroy(self, instance):
        # Log the deletion of an ActivityLog
        ActivityLog.objects.create(
            user=instance.user,
            action_user=self.request.user,
            action='delete',
            object_id=instance.id,
            content_type='Activity-Log',
        )
        instance.delete()