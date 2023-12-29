from rest_framework import serializers

from .models import Resources, Type


class ResourcesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = "__all__"


class ResourcesSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.StringRelatedField(source='sender.full_name')
    receiver_full_name = serializers.StringRelatedField(source='receiver.full_name')

    class Meta:
        model = Resources
        fields = "__all__"
