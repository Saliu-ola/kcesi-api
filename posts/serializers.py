from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class OrganizationPostSerializer(serializers.Serializer):
    organization_id = serializers.CharField(max_length=15,min_length=15, required=True)
