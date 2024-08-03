from rest_framework import serializers
from .models import *
from accounts.models import User
from group.models import *
from accounts.serializers import ListUserSerializer


LIBRARY_CHOICES = [
    ('AI', 'AI '),
    ('FILES', 'FILES '),
    ]


class GroupLeaderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    user_details = ListUserSerializer(source='user',read_only = True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    

    class Meta:
        model = GroupLeader
        fields = ['id', 'user_details', 'user' ,'group', 'assigned_at']


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
    is_group_leader = serializers.BooleanField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    status = serializers.ChoiceField(choices=LibraryFile.STATUS_CHOICES)
    group_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = LibraryFile
        fields = ['id', 'group', 'group_name', 'filename', 'user_name', 'full_name', 'filedescription', 'user', 'status', 'datetime', 'file_url', 'is_synchronize', 'is_group_leader']
        # fields = '__all__'

    def get_group_name(self, obj)-> str:
        return obj.group.title

    def get_user_name(self, obj)-> str:
        return obj.user.username

    def get_full_name(self, obj)-> str:
        return f"{obj.user.first_name} {obj.user.last_name}"

    # def validate_file_url(self, value):
    #      if not value.lower().endswith('.pdf'):
    #         raise serializers.ValidationError("File URL must point to a PDF file.")

    def validate_file_url(self, value):
        if value and not value.lower().endswith(".pdf"):
            raise serializers.ValidationError("File URL must point to a PDF file.")
        return value

    # def validate(self, data):
    #     group = data.get('group')
    #     user = data.get('user')

    #     # Custom validation: Ensure the user is a member of the group
    #     if not UserGroup.objects.filter(user=user, groups=group).exists():
    #         raise serializers.ValidationError("The user is not a member of the group.")

    #     return data

class SyncLibraryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryFile
        fields = ['group', 'filename', 'filedescription', 'user', 'status', 'datetime', 'file_url', 'is_synchronize']


class GroupGroupLeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'title', 'content', 'organization_id', 'created_at', 'updated_at', 'related_terms', 'related_terms_library_b']


class GroupLibrariesSerializer(serializers.ModelSerializer):
    related_terms = serializers.ListField(child=serializers.CharField(), required=False)
    related_terms_library_b = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Group
        fields = ['related_terms', 'related_terms_library_b']
