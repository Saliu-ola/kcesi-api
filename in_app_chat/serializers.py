from rest_framework import serializers

from .models import InAppChat


class InAppChatSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.StringRelatedField(source='sender.full_name')
    receiver_full_name = serializers.StringRelatedField(source='receiver.full_name')

    class Meta:
        model = InAppChat
        fields = "__all__"
