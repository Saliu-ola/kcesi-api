from rest_framework import serializers

from .models import InAppChat


class InAppChatSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.StringRelatedField(source='sender.full_name')
    receiver_full_name = serializers.StringRelatedField(source='receiver.full_name')
    group_name = serializers.StringRelatedField(
        source='group.title',
    )
    organization_name = serializers.StringRelatedField(
        source='organization.name',
    )


    def create(self, validated_data):
        validated_data['message'] = validated_data['message'] + " + (corect)"
        return super().create(validated_data)

    class Meta:
        model = InAppChat
        fields = "__all__"
