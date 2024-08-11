from rest_framework import serializers

from groupleader.models import LibraryOption

from .models import Group, UserGroup
from organization.models import Organization
from accounts.models import User
from rest_framework.validators import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from django.db.models import Q
from simpleblog.ai import get_cleaned_and_lematized_terms
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from groupleader.models import GroupLeader

class GroupSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField(
        read_only=True, method_name="get_organization_name"
    )
    related_terms = serializers.JSONField(read_only=True)
    group_leader = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = "__all__"

    def create(self, validated_data):
        title = validated_data["title"]
        organization_id = validated_data["organization_id"]

        if Group.objects.filter(
            Q(title__iexact=title) & Q(organization_id__iexact=organization_id)
        ).exists():
            raise serializers.ValidationError(
                f"{title} group already exists for the organization"
            )

        try:
            with transaction.atomic():
                group = super().create(validated_data)
                related_terms = get_cleaned_and_lematized_terms(group.content)

                if not related_terms:
                    raise serializers.ValidationError(
                        "No related words found for the group content"
                    )
                group.related_terms = related_terms
                group.save()
                # Create a LibraryOption instance for the new group

                LibraryOption.objects.create(group=group, library_type="AI")
        except IntegrityError as e:
            # Handle specific database integrity errors
            raise serializers.ValidationError("Database integrity error: " + str(e))
        except Exception as e:
            # Handle other exceptions
            print(str(e))
            raise serializers.ValidationError(
                "Kindly try again,unable to generate terminologies for the group"
            )

        return group

    def get_organization_name(self, instance):
        return Organization.objects.get(organization_id=instance.organization_id).name
    
    def get_group_leader(self, instance):
        try:
            group_leader = GroupLeader.objects.get(group=instance)
            return {
                'id': group_leader.user.id,
                'username': group_leader.user.username,
                'email': group_leader.user.email,
                'first_name': group_leader.user.first_name,
                'last_name': group_leader.user.last_name,
                'assigned_at': group_leader.assigned_at
            }
        except GroupLeader.DoesNotExist:
            return None


class GroupAISerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ["id", "content"]


class UserGroupListSerializer(serializers.ModelSerializer):
    full_name = serializers.StringRelatedField(source="user.full_name")
    organization_name = serializers.StringRelatedField(source="user.organization_name")
    organization_id = serializers.StringRelatedField(source="user.organization_id")
    group_titles = serializers.StringRelatedField(
        source="groups", many=True, read_only=True
    )

    class Meta:
        model = UserGroup
        fields = "__all__"



class UsersInGroupListSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source="user.username")
    full_name = serializers.StringRelatedField(source="user.full_name")
    organization_name = serializers.StringRelatedField(source="user.organization_name")
    organization_id = serializers.StringRelatedField(source="user.organization_id")

    class Meta:
        model = UserGroup
        fields = ['user', 'organization_id', 'organization_name', 'username', 'full_name']



class UserGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = "__all__"

    def validate(self, data):
        user = data["user"]
        groups = data["groups"]

        user_organization_id = user.organization_id

        if user_organization_id is None:
            raise serializers.ValidationError("User has no organization")

        invalid_groups = [
            group.title
            for group in groups
            if group.organization_id != user_organization_id
        ]

        if invalid_groups:
            raise serializers.ValidationError(
                f"The following groups do not belong to {user.organization_name}: {', '.join(invalid_groups)}"
            )

        return data

    def create(self, validated_data):
        if UserGroup.objects.filter(user=validated_data["user"]).exists():
            raise serializers.ValidationError(
                "Cannot create more than one UserGroup for a user"
            )

        return super().create(validated_data)


class UpdateUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ["groups", "user"]

    def validate(self, data):
        user = data["user"]
        groups = data["groups"]

        user_organization_id = user.organization_id

        if user_organization_id is None:
            raise serializers.ValidationError("User has no organization")

        invalid_groups = [
            group.title
            for group in groups
            if group.organization_id != user_organization_id
        ]

        if invalid_groups:
            raise serializers.ValidationError(
                f"The following groups do not belong to {user.organization_name}: {', '.join(invalid_groups)}"
            )

        return data


class GrouppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "title", "organization_id"]


class UserGroupSerializer(serializers.ModelSerializer):
    groups = GrouppSerializer(many=True)

    class Meta:
        model = UserGroup
        fields = "__all__"


class UsersInGroupListSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source="user.username")
    full_name = serializers.StringRelatedField(source="user.full_name")
    organization_name = serializers.StringRelatedField(source="user.organization_name")
    organization_id = serializers.StringRelatedField(source="user.organization_id")
    # user_groups = serializers.SerializerMethodField(method_name='get_user_groups')

    class Meta:
        model = UserGroup
        fields = ['user', 'organization_id', 'organization_name', 'username', 'full_name']#, 'user_groups']
    
    # def get_user_groups(self, instance):
    #     try:
    #         user_group_object =  UserGroupCreateSerializer(UserGroup.objects.get(user=instance.user)).data
    #         data = [{
            
    #                 "group_id":group,
    #                 "group_name":Group.objects.get(pk=group).title,
    #         }  for group in user_group_object["groups"]]

    #         return data
             
    #     except ObjectDoesNotExist:
    #         return None
