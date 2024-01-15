from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    creator_full_name = serializers.StringRelatedField(source='creator.full_name')

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["creator", "organization", "group"]
