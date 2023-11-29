from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError

from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=80)
    username = serializers.CharField(max_length=45)
    password = serializers.CharField(min_length=8, write_only=True) 
    first_name = serializers.CharField(max_length=45)
    last_name= serializers.CharField(max_length=45)
    role_id = serializers.IntegerField()
    group_id = serializers.IntegerField()
    is_superuser = serializers.BooleanField()
    is_staff= serializers.BooleanField()

    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name", 
                  "group_id", "role_id", "is_superuser", "is_staff"]






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
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

