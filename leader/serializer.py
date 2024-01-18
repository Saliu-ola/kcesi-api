# serializers.py
from rest_framework import serializers
from .models import Socialization, Externalization, Combination, Internalization


class SocializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socialization
        fields = '__all__'


class ExternalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Externalization
        fields = '__all__'


class CombinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Combination
        fields = '__all__'


class InternalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internalization
        fields = '__all__'
