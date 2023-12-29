from rest_framework import serializers

from .models import Forum


class ForumSerializer(serializers.ModelSerializer):
    user_full_name = serializers.StringRelatedField(source='user.full_name')

    class Meta:
        model = Forum
        fields = "__all__"
