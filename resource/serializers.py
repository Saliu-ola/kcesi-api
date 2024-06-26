from rest_framework import serializers

from .models import Resources
import cloudinary.uploader
from organization.models import Organization
from group.models import Group
from platforms.models import Platform
from accounts.models import User
from organization.models import Organization
from group.models import Group
from rest_framework.validators import ValidationError


MAXIMUM_SIZE_UPLOAD = 2 * 1024 * 1024  # 2MB
RESOURCE_TYPES = (
    ("AUDIO", "AUDIO"),
    ("VIDEO", "VIDEO"),
    ("IMAGE", "IMAGE"),
    ("DOCUMENT", "DOCUMENT"),
    ("OTHERS", "OTHERS"),
)


class ResourcesSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.StringRelatedField(source='sender.full_name')
    receiver_full_name = serializers.StringRelatedField(source='receiver.full_name')

    class Meta:
        model = Resources
        fields = "__all__"


class CreateResourcesSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True, write_only=True)
    title = serializers.CharField(required=True)
    type = serializers.ChoiceField(RESOURCE_TYPES, required=True)

    class Meta:
        model = Resources
        fields = [
            "id",
            "title",
            "file",
            "type",
            "group",
            "organization",
            "platform",
            "sender",
            "receiver",
            "size",
            "media_url",
            "cloud_id",
        ]
        read_only_fields = ["id", "media_url", "cloud_id", "size"]

    def validate_file(self, value):
        if value.size > MAXIMUM_SIZE_UPLOAD:
            raise ValidationError("File size must not be more than 2MB")
        return value

    def create(self, validated_data):
        file = validated_data.pop('file')  # Extract 'file' from validated_data

        # Upload the file to Cloudinary or your desired storage
        upload_result = cloudinary.uploader.upload(file, resource_type='raw')

        # Create a new Resources instance with the other fields
        instance = Resources.objects.create(
            media_url=upload_result["url"],
            cloud_id=upload_result["public_id"],
            size=upload_result["bytes"],
            **validated_data,
        )

        return instance

    def update(self, instance, validated_data):
        file = validated_data.pop('file', None)  # Extract 'file' from validated_data

        if file:
            # Delete the old file in Cloudinary
            cloudinary.uploader.destroy(instance.cloud_id)

            # Upload the new file to Cloudinary or your desired storage
            upload_result = cloudinary.uploader.upload(file, resource_type='raw')

            # Update the media_url and cloud_id with the new values
            instance.media_url = upload_result["url"]
            instance.cloud_id = upload_result["public_id"]
            instance.size = upload_result["bytes"]

        # Update other fields as needed
        instance.title = validated_data.get('title', instance.title)
        instance.type = validated_data.get('type', instance.type)
        instance.platform = validated_data.get('platform', instance.platform)
        instance.organization = validated_data.get('organization', instance.organization)
        instance.group = validated_data.get('group', instance.group)
        instance.sender = validated_data.get('sender', instance.sender)
        instance.receiver = validated_data.get('receiver', instance.receiver)

        instance.save()
        return instance
