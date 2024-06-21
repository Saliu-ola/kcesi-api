from rest_framework import serializers

from .models import Forum, ForumComment,CommentReplies


class ForumSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    group_name = serializers.StringRelatedField(
        source='group.title',
    )
    organization_name = serializers.StringRelatedField(
        source='organization.name',
    )
    category_name = serializers.StringRelatedField(
        source='category.name',
    )

    resources_url = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='media_url', source='resources'
    )

    class Meta:
        model = Forum
        fields = "__all__"


class ForumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = [
            "id",
            "topic",
            "category",
            "content",
            "organization",
            "group",
            "score",
            "resources",
            "start_time",
            "end_time",
            "user",
        ]
        read_only_fields = ["id"]


class ForumCommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = ForumComment
        fields = "__all__"


class CommentReplySerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = CommentReplies
        fields = "__all__"
