from django.db import models
from platforms.models import Platform
from organization.models import Organization
from group.models import Group
from accounts.models import User
from cloudinary.models import CloudinaryField


RESOURCE_TYPES = (
    ("AUDIO", "AUDIO"),
    ("VIDEO", "VIDEO"),
    ("IMAGE", "IMAGE"),
    ("DOCUMENT", "DOCUMENT"),
    ("OTHERS", "OTHERS"),
)


class Resources(models.Model):
    title = models.CharField(max_length=50, null=True)
    size = models.IntegerField(null=True)
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default="IMAGE")
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="platform_resources", null=True
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_resources", null=True
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, related_name="group_resources"
    )

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="sender_resources"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver_resources", null=True
    )
    media_url = models.CharField(max_length=255, blank=True, null=True)
    cloud_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.title or " "

    class Meta:
        ordering = ["-created_at"]



class ResourceFileSize(models.Model):

    file_type = models.CharField(max_length=10, choices=RESOURCE_TYPES, unique=True)
    max_size = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.max_size} Megabyte"



class ResourceDownload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resource_downloads")
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE, related_name="downloads")
    resource_type = models.CharField(max_length=8, choices=RESOURCE_TYPES)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="org_resource_downloads")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_resource_downloads")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'resource']

    def __str__(self):
        return f"{self.user} downloaded {self.resource}"