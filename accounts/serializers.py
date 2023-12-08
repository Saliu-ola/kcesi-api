from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError

from .models import User


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    email = serializers.EmailField()
    group_id = serializers.IntegerField(default=0)
    role_id = serializers.IntegerField(default=0)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "phone",
            "first_name",
            "last_name",
            "group_id",
            "role_id",
            "is_superuser",
            "is_staff",
            "organization_id",
            "organization_name",
        ]

    def validate(self, attrs):
        email_exists = User.objects.filter(email=attrs["email"]).exists()

        if email_exists:
            raise ValidationError("Email has already been used")

        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = super().create(validated_data)

        user.set_password(password)

        user.save()

        Token.objects.create(user=user)

        return user


class CurrentUserPostsSerializer(serializers.ModelSerializer):
    posts = serializers.HyperlinkedRelatedField(
        many=True, view_name="post_detail", queryset=User.objects.all()
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "posts"]


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
