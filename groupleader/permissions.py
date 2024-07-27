from rest_framework.permissions import BasePermission
from .models import GroupLeader



class IsGroupLeaderPermission(BasePermission):
    """
    Custom permission to check if a user is the leader of a specific group.
    """
    def has_permission(self, request, view):
        group_id = view.kwargs.get('group_id')  # Assuming d group_id is passed in the URL
        if not group_id:
            return False
        
        return GroupLeader.objects.filter(user=request.user, group_id=group_id).exists()

    def has_object_permission(self, request, view, obj):
        return GroupLeader.objects.filter(user=request.user, group=obj).exists()
    


class IsLeaderOfAnyGroup(BasePermission):
    """
    Custom permission to check if a user is the leader of any group.
    """
    def has_permission(self, request, view):
        return GroupLeader.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        return GroupLeader.objects.filter(user=request.user).exists()