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


class GetLibraryFileSerializer(serializers.ModelSerializer):
    is_group_leader = serializers.BooleanField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)
    group_names = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    status = serializers.ChoiceField(choices=LibraryFile.STATUS_CHOICES)
    user_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = LibraryFile
        fields = [
            "id",
            "group",
            "group_names",
            "filename",
            "user_name",
            "full_name",
            "filedescription",
            "user",
            "status",
            "datetime",
            "file_url",
            "is_synchronize",
            "is_group_leader",
        ]

    def get_group_names(self, obj):
        return [group.title for group in obj.group.all()]

    def get_user_name(self, obj) -> str:
        return obj.user.username

    def get_full_name(self, obj) -> str:
        return f"{obj.user.first_name} {obj.user.last_name}"

    def validate_file_url(self, value):
        if value and not value.lower().endswith(".pdf"):
            raise serializers.ValidationError("File URL must point to a PDF file.")
        return value

    def validate(self, data):
        group = data.get("group")
        user = data.get("user")

        # Custom validation: Ensure the user is a member of the group
        if not UserGroup.objects.filter(user=user, groups__in=group).exists():
            raise serializers.ValidationError(
                "The user is not a member of one or more groups."
            )

        return data


class LibraryFileSerializer(serializers.ModelSerializer):
    is_group_leader = serializers.BooleanField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(),many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    status = serializers.ChoiceField(choices=LibraryFile.STATUS_CHOICES,required=False)
    # group_name = serializers.SerializerMethodField()
    group_name = serializers.CharField(source="group.all.title", read_only=True)
    # user_name = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = LibraryFile
        fields = ['id', 'group', 'group_name', 'filename', 'user_name', 'full_name', 'filedescription', 'user', 'status', 'datetime', 'file_url', 'is_synchronize', 'is_group_leader']
        # fields = '__all__'

    # def get_group_name(self, obj) -> str:
    #     return ", ".join([group.title for group in obj.group])

    # def get_user_name(self, obj)-> str:
    #     return obj.user.username

    # def get_full_name(self, obj)-> str:
    #     return f"{obj.user.first_name} {obj.user.last_name}"

    def get_full_name(self, obj):
        return obj.user.get_full_name

    def validate_file_url(self, value):
        if value and not value.lower().endswith('.pdf'):
            raise serializers.ValidationError("File URL must point to a PDF file.")

        return value

    def validate(self, data):
        groups = data.get('group')
        user = data.get('user')

        # Iterate through the group list and check membership for each group
        for group in groups:
            if not UserGroup.objects.filter(user=user, groups=group.id).exists():
                raise serializers.ValidationError(f"The user is not a member of group {group.title}.")

        return data


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
