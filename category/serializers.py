from rest_framework import serializers

from .models import Category
from django.db.models import Q


class CategorySerializer(serializers.ModelSerializer):
    creator_full_name = serializers.StringRelatedField(source='creator.full_name')

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["creator"]

    def validate(self, data):
        user = self.context["request"].user
        group = data['group']

        user_organization_id = user.organization_id

        if user_organization_id is None:
            raise serializers.ValidationError("User has no organization")

        if group.organization_id != user_organization_id:
            raise serializers.ValidationError(
                f"The {group.title } group, with id {group.pk} do not belong to {user.organization_name} organization"
            )

        return data

    def create(self, validated_data):
        name = validated_data["name"]
        organization = (validated_data["organization"])
        group = validated_data["group"]

        if Category.objects.filter(
            Q(name__iexact=name) & Q(organization=organization) & Q(group=group)
        ).exists():
            raise serializers.ValidationError(
                f"{name} category already exists for the organization with regards to the group"
            )

        return super().create(validated_data)
