from rest_framework import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import shutil
import uuid

from .models import Resources, ResourceDownload
import cloudinary.uploader
from organization.models import Organization
from group.models import Group
from platforms.models import Platform
from accounts.models import User
from organization.models import Organization
from group.models import Group
from rest_framework.validators import ValidationError
from .models import ResourceFileSize


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

    def get_unique_filename(self, original_filename):
        # Get the file extension
        ext = os.path.splitext(original_filename)[1]
        # Generate a unique filename using UUID
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        return unique_filename

    def save_file(self, file):
        # Ensure media directory exists
        media_dir = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_dir, exist_ok=True)

        # Generate a unique filename
        unique_filename = self.get_unique_filename(file.name)
        
        # Full path where the file will be saved
        full_path = os.path.join(media_dir, unique_filename)
        
        # Save the file
        with open(full_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Return the relative path for URL generation
        return f"media/{unique_filename}"

    def get_full_url(self, file_path):
        base_url = getattr(settings, 'BASE_URL', 'http://knowshare.info:8000')
        # Ensure proper path format
        file_path = file_path.replace('\\', '/').replace('//', '/')
        return f"{base_url}/{file_path}"

    def create(self, validated_data):
        file = validated_data.pop('file')
        
        # Save the file and get its path
        file_path = self.save_file(file)
        
        # Get the full URL
        file_url = self.get_full_url(file_path)
        
        # Create the resource
        instance = Resources.objects.create(
            media_url=file_url,
            cloud_id=file_path,
            size=file.size,
            **validated_data,
        )

        return instance

    def update(self, instance, validated_data):
        file = validated_data.pop('file', None)

        if file:
            # Delete the old file if it exists
            if instance.cloud_id:
                old_file_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(instance.cloud_id))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Save the new file
            file_path = self.save_file(file)
            file_url = self.get_full_url(file_path)
            
            # Update instance
            instance.media_url = file_url
            instance.cloud_id = file_path
            instance.size = file.size

        # Update other fields
        instance.title = validated_data.get('title', instance.title)
        instance.type = validated_data.get('type', instance.type)
        instance.platform = validated_data.get('platform', instance.platform)
        instance.organization = validated_data.get('organization', instance.organization)
        instance.group = validated_data.get('group', instance.group)
        instance.sender = validated_data.get('sender', instance.sender)
        instance.receiver = validated_data.get('receiver', instance.receiver)

        instance.save()
        return instance




class ResourceFileSizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceFileSize
        fields = ['file_type', 'max_size']


    def validate_max_size(self, value):
        #maximum accceptable size for any file currently 1024mb (1GB)

        if value < 1 or value > 1024:
            raise serializers.ValidationError("Max size must be between 1 MB and 1024 MB (1 GB).")
        return value



class ResourceDownloadSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source='resource.title', read_only=True)  
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ResourceDownload
        fields = ['id', 'user', 'username', 'resource', 'resource_name', 'resource_type', 'group', 'organization', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']



class ResourceDownloadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceDownload
        fields = ['resource', 'resource_type', 'group', 'organization']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)