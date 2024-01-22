from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError
from group.serializers import GroupSerializer


from .models import User
from group.models import Group

EXISITING_EMAIL_ERROR = "Email has already been used"


class ListUserSerializer(serializers.ModelSerializer):
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
            "gender",
            "last_name",
            "group_id",
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

    def to_representation(self, instance):
        group_id = instance.group_id
        if group_id is not None:
            group_identifier = Group.objects.filter(pk=group_id).first()

            if group_identifier:
                instance_data = super().to_representation(instance)
                instance_data["group_detail"] = {
                    "id": group_identifier.pk,
                    "title": group_identifier.title,
                    "content": group_identifier.content,
                }
                return instance_data

        return super().to_representation(instance)


class UserSignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    role_id = serializers.IntegerField(default=0)
    is_superuser = serializers.BooleanField(default=False)

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
            "group_id",
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
            "groups": [
                {"group": {"id": group.id, "title": group.title, "content": group.content}}
                for group in instance["groups"]
            ],
        }
