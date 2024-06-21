from rest_framework import serializers

from .models import Organization
from rest_framework.validators import ValidationError


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"

   
