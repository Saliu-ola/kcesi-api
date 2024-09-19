from rest_framework import serializers
from django.db import transaction
from .models import Forum, ForumComment,CommentReplies
from topics.models import ForumTopic

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

    def create(self, validated_data):
        
        with transaction.atomic():
            resources_data = validated_data.pop('resources', [])

            topic_title = validated_data['topic']
            forum_topic, created = ForumTopic.objects.get_or_create(
                title=topic_title,
                defaults={
                    'forum': None,  
                    'group': validated_data.get('group'),
                    'organization': validated_data.get('organization'),
                    # 'author': validated_data.get('user'),
                    'author': self.context['request'].user,
                }
            )

            forum = Forum.objects.create(**validated_data)
            
            if created:
                forum_topic.forum = forum
                forum_topic.save()
            else:
                pass
                

            return {
                'forum': forum,
                'forum_topic': forum_topic,
                'forum_topic_created': created
            }



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
