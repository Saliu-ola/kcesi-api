from rest_framework import serializers
from .models import *
from accounts.models import User
from group.models import *

LIBRARY_CHOICES = [
    ('AI', 'AI '),
    ('FILES', 'FILES '),
    ]


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
    library_type = serializers.ChoiceField(LIBRARY_CHOICES, required=True)

    class Meta:
        model = LibraryOption
        fields = ['id', 'library_type' , 'group']



class LibraryFileSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    status = serializers.ChoiceField(choices=LibraryFile.STATUS_CHOICES)

    class Meta:
        model = LibraryFile
        fields = '__all__'

    def validate(self, data):
        group = data.get('group')
        user = data.get('user')
        
        # Custom validation: Ensure the user is a member of the group
        if not UserGroup.objects.filter(user=user, groups=group).exists():
            raise serializers.ValidationError("The user is not a member of the group.")
        
        return data
    



class LibraryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryFile
        fields = ['group', 'filename', 'filedescription', 'user', 'status', 'datetime', 'file_url', 'is_synchronize']
