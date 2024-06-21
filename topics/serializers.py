from rest_framework import serializers

from .models import Topic


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
