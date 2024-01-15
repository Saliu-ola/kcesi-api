from rest_framework import serializers

from .models import Group
from organization.models import Organization


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        organization_name = Organization.objects.get(organization_id=instance.organization_id).name
        instance_data["organization_name"] = organization_name
        return instance_data
