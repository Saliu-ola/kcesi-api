from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError
from group.serializers import UserGroupCreateSerializer

from .models import User
from group.models import Group, UserGroup
from django.core.exceptions import ObjectDoesNotExist
from organization.models import Organization

EXISITING_EMAIL_ERROR = "Email has already been used"


class ListUserSerializer(serializers.ModelSerializer):
    user_groups = serializers.SerializerMethodField(method_name='get_user_groups')
    organization = serializers.SerializerMethodField(method_name="get_user_organization")
    active_for_chat = serializers.SerializerMethodField(method_name="check_user_online")

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "date_of_birth",
            "first_name",
            "gender",
            "last_name",
            "first_group_id",
            "role_id",
            "is_superuser",
            "is_staff",
            "organization",
            "organization_id",
            "organization_name",
            "image_url",
            "cloud_id",
            "user_groups",
            "active_for_chat",
            "created_at",
            "updated_at",
            "is_verified",
        ]

    def get_user_groups(self, instance):
        try:
            user_group_object =  UserGroupCreateSerializer(UserGroup.objects.get(user=instance)).data
            data = [{
            
                    "group_id":group,
                    "group_name":Group.objects.get(pk=group).title,
            }  for group in user_group_object["groups"]]

            return data
             
        except ObjectDoesNotExist:
            return None

    def check_user_online(self, instance):
        return instance.is_active_for_chat

    def get_user_organization(self, instance):
        try:
            if instance.organization_id:
                return Organization.objects.get(organization_id=instance.organization_id).pk
        except ObjectDoesNotExist:
            return None
    

class UserSignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    role_id = serializers.IntegerField(default=0)
    is_superuser = serializers.BooleanField(default=False)
    first_group_id = serializers.IntegerField(default=0)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "phone",
            "date_of_birth",
            "first_name",
            "last_name",
            "first_group_id",
            "gender",
            "role_id",
            "is_superuser",
            "is_staff",
            "organization_id",
            "organization_name",
            "image_url",
            "cloud_id",
            "created_at",
            "updated_at",
            "is_verified",
        ]
        read_only_fields = [
            "id",
            "is_staff",
            "image_url",
            "cloud_id",
            "created_at",
            "updated_at",
            "is_verified",
        ]

    def validate(self, attrs):
        email_exists = User.objects.filter(email=attrs["email"]).exists()

        if email_exists:
            raise ValidationError(EXISITING_EMAIL_ERROR)

        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = super().create(validated_data)

        user.set_password(password)

        user.save()

        Token.objects.create(user=user)

        return user


class UpdateUserImage(serializers.Serializer):
    image = serializers.ImageField(required=True)


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class VerifyTokenSerializer(serializers.Serializer):
    """Serializer for token verification"""

    token = serializers.CharField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    """serializer to initiate password reset invite"""

    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """serializer to reset password"""

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True)


class OrganizationByNameInputSerializer(serializers.Serializer):
    organization_id = serializers.CharField(read_only=True)
    organization_name = serializers.CharField(
        required=True,
    )


class OrganizationByIDInputSerializer(serializers.Serializer):
    organization_id = serializers.CharField()

    def validate(self, attrs):
        organization_id = attrs["organization_id"]

        if not organization_id:
            return ValidationError({"message": "organization_id parameter is required"})

        return super().validate(attrs)

    def to_representation(self, instance):
        return {
            "organization_id": instance["organization_id"],
            "organization_name": instance["organization_name"],
            "groups": [instance["groups"]],
        }
