from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError

from .models import User

EXISITING_EMAIL_ERROR = "Email has already been used"


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }


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
            "role_id",
            "is_superuser",
            "is_staff",
            "organization_id",
            "organization_name",
            "created_at",
            "updated_at",
            "is_verified",
        ]
        read_only_fields = [
            "id",
            "is_staff",
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


# class CurrentUserPostsSerializer(serializers.ModelSerializer):
#     posts = serializers.HyperlinkedRelatedField(
#         many=True, view_name="post_detail", queryset=User.objects.all()
#     )


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


class OrganizationByIDInputSerializer(serializers.Serializer):
    organization_id = serializers.CharField(max_length=15, min_length=15, required=True)
    organization_name = serializers.CharField(read_only=True)


class OrganizationByNameInputSerializer(serializers.Serializer):
    organization_id = serializers.CharField(read_only=True)
    organization_name = serializers.CharField(
        required=True,
    )
