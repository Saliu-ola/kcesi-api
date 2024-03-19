from rest_framework import serializers

from .models import Forum, ForumComment


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

    resources = serializers.SlugRelatedField(many=True, read_only=True, slug_field='media_url')

    class Meta:
        model = Forum
        fields = "__all__"


class ForumCommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = ForumComment
        fields = "__all__"
