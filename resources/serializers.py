from rest_framework import serializers

from .models import Resources, ResourcesType


class ResourcesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourcesType
        fields = "__all__"


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = "__all__"
