from rest_framework import serializers

from .models import Blog, Comment


class BlogCreateSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(
        source='author.full_name',
    )
    resources = serializers.SlugRelatedField(many=True, read_only=True, slug_field='media_url')

    class Meta:
        model = Blog
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = Comment
        fields = "__all__"
