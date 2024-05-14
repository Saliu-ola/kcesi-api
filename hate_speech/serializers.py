from rest_framework import serializers
from .models import BadWord

class BadWordSerializer(serializers.ModelSerializer):

    class Meta:
        model = BadWord
        fields = "__all__"

    def create(self, validated_data):

        if BadWord.objects.exists():
            raise serializers.ValidationError("Only one collection is allowed to be saved.you can only remove or add")
        return super().create(validated_data)
