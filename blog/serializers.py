from rest_framework import serializers

from .models import Blog, Comment


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
    resources = serializers.SlugRelatedField(many=True, read_only=True, slug_field='media_url')

    class Meta:
        model = Blog
        fields = "__all__"


class BlogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ["id", "topic", "category", "content", "organization", "group", "resources"]
        read_only_fields = ["id"]


class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = Comment
        fields = "__all__"
