from rest_framework import serializers

from .models import Forum, ForumComment


class ForumSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = Forum
        fields = "__all__"


class ForumCommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = ForumComment
        fields = "__all__"
