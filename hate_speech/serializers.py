from rest_framework import serializers
from .models import BadWord

from rest_framework import serializers


class BadWordSerializer(serializers.ModelSerializer):
    related_terms = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    class Meta:
        model = BadWord
        fields = "__all__"

    def create(self, validated_data):

        if BadWord.objects.count() > 1:
            raise serializers.ValidationError("Only one collection is allowed to be saved.you can only remove or add")
        return super().create(validated_data)
