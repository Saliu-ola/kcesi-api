from rest_framework import serializers

from .models import Topic


class TopicSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(
        source='author.full_name',
    )

    class Meta:
        model = Topic
        fields = "__all__"
