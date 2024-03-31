from rest_framework import serializers

from .models import Blog, Comment, BlogCommentReplies


class BlogListSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(
        source='author.full_name',
    )
    group_name = serializers.StringRelatedField(
        source='group.title',
    )
    organization_name = serializers.StringRelatedField(
        source='organization.name',
    )
    category_name = serializers.StringRelatedField(
        source='category.name',
    )
    resources_url = serializers.SlugRelatedField(many=True, read_only=True, slug_field='resources.media_url')

    class Meta:
        model = Blog
        fields = "__all__"


class BlogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "id",
            "topic",
            "category",
            "content",
            "organization",
            "group",
            "resources"
        ]
        read_only_fields = ["id"]


class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = Comment
        fields = "__all__"


class BlogCommentReplySerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = BlogCommentReplies
        fields = "__all__"
