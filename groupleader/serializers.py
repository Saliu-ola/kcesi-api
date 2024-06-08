from rest_framework import serializers
from .models import *
from accounts.models import User
from group.models import *

class GroupLeaderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = GroupLeader
        fields = ['id', 'user', 'group', 'assigned_at']


    # def to_internal_value(self, data):
    #     group_id = data.get('group')
    #     if group_id:
    #         self.fields['user'].queryset = User.objects.filter(user_groups__groups__id=group_id)
    #     return super().to_internal_value(data)
    
    def validate(self, data):
        user = data.get('user')
        group = data.get('group')

        # Ensure the user is part of the group
        if not UserGroup.objects.filter(user=user, groups=group).exists():
            raise serializers.ValidationError("The user is not a member of the group.")

        if GroupLeader.objects.filter(user=user, group=group).exists():
            raise serializers.ValidationError("This user is already a leader of the group.")
        
        return data
    


class LibraryOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryOption
        fields = '__all__'