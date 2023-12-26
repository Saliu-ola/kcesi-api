from rest_framework import serializers

from .models import InAppChat


class InAppChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = InAppChat
        fields = "__all__"
