# serializers.py
from rest_framework import serializers
from .models import Socialization, Externalization, Combination, Internalization
from rest_framework.validators import UniqueTogetherValidator

unique_together_message = "Activity score for this organization and group already exists."


class SocializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socialization
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Socialization.objects.all(),
                fields=['organization', 'group'],
                message=unique_together_message,
            )
        ]


class ExternalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Externalization
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Externalization.objects.all(),
                fields=['organization', 'group'],
                message=unique_together_message,
            )
        ]


class CombinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Combination
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Combination.objects.all(),
                fields=['organization', 'group'],
                message=unique_together_message,
            )
        ]


class InternalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internalization
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Internalization.objects.all(),
                fields=['organization', 'group'],
                message=unique_together_message,
            )
        ]
