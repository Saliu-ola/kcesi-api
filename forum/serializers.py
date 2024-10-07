from rest_framework import serializers
from django.db import transaction
from .models import Forum, ForumComment, CommentReplies, ForumRead
from topics.models import ForumTopic


class ForumSerializer(serializers.ModelSerializer):
    # user_full_name = serializers.StringRelatedField(source='user.first_name')
    user_full_name = serializers.SerializerMethodField()

    group_name = serializers.StringRelatedField(
        source="group.title",
    )
    organization_name = serializers.StringRelatedField(
        source="organization.name",
    )
    category_name = serializers.StringRelatedField(
        source="category.name",
    )

    resources_url = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="media_url", source="resources"
    )

    class Meta:
        model = Forum
        fields = "__all__"

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


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
            resources_data = validated_data.pop("resources", [])

            topic_title = validated_data["topic"]
            forum_topic, created = ForumTopic.objects.get_or_create(
                title=topic_title,
                defaults={
                    "forum": None,
                    "group": validated_data.get("group"),
                    "organization": validated_data.get("organization"),
                    # 'author': validated_data.get('user'),
                    "author": self.context["request"].user,
                },
            )

            forum = Forum.objects.create(**validated_data)

            if created:
                forum_topic.forum = forum
                forum_topic.save()
            else:
                pass

            return {
                "forum": forum,
                "forum_topic": forum_topic,
                "forum_topic_created": created,
            }


class ForumCommentSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source="user.full_name")

    class Meta:
        model = ForumComment
        fields = "__all__"


class CommentReplySerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source="user.full_name")

    class Meta:
        model = CommentReplies
        fields = "__all__"


class ForumReadSerializer(serializers.ModelSerializer):
    forum_topic = serializers.CharField(source="forum.topic", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ForumRead
        fields = [
            "id",
            "user",
            "username",
            "forum",
            "forum_topic",
            "group",
            "organization",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]


class ForumReadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumRead
        fields = ["forum", "group", "organization"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
