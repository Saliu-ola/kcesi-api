from rest_framework import serializers
from .models import Feedback


class FeedbackListSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(
        source='author.full_name',
    )
    concerned_group_name = serializers.StringRelatedField(
        source='concerned_group.title',
    )
    concerned_organization_name = serializers.StringRelatedField(
        source='concerned_organization.name',
    )
    concerned_platform_name = serializers.StringRelatedField(
        source='concerned_platform.name',
    )

    class Meta:
        model = Feedback
        fields = "__all__"


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "id",
            "content",
            "recipent_type",
            "concerned_organization",
            "concerned_group",
            "concerned_platform",
           
        ]
        read_only_fields = ["id"]
