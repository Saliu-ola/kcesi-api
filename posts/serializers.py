from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    organization_id = serializers.StringRelatedField(source='author.organization_id')

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = [
            "id",
            "organization_id",
            "author",
        ]
