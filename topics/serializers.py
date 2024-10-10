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


class CombinedTopicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.StringRelatedField()
    # author_name = serializers.StringRelatedField()
    organization = serializers.StringRelatedField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    author_full_name = serializers.SerializerMethodField()
    topic_type = serializers.SerializerMethodField()

    def get_topic_type(self, obj):
        return 'blog' if isinstance(obj, BlogTopic) else 'forum'
    
    def get_author_full_name(self, obj):
        return obj.author.full_name