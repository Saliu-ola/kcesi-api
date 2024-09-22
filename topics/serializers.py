from rest_framework import serializers

from .models import Topic, BlogTopic, ForumTopic


class TopicSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(
        source='author.full_name',
    )
    group_name = serializers.StringRelatedField(
        source='group.title',
    )
    organization_name = serializers.StringRelatedField(
        source='organization.name',
    )

    class Meta:
        model = Topic
        fields = "__all__"


class BlogTopicSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source='author.full_name')
    group_name = serializers.StringRelatedField(source='group.name')
    organization_name = serializers.StringRelatedField(source='organization.name')

    class Meta:
        model = BlogTopic
        fields = "__all__"

# Serializer for ForumTopic
class ForumTopicSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source='author.full_name')
    group_name = serializers.StringRelatedField(source='group.name')
    organization_name = serializers.StringRelatedField(source='organization.name')

    class Meta:
        model = ForumTopic
        fields = "__all__"
