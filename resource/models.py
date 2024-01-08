from django.db import models
from platforms.models import Platform
from organization.models import Organization
from group.models import Group
from accounts.models import User
from cloudinary.models import CloudinaryField


class Type(models.Model):
    name = models.CharField(max_length=50, null=True)

    def __str__(self) -> str:
        return self.name


class Resources(models.Model):
    title = models.CharField(max_length=50, null=True)
    size = models.IntegerField(null=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name="type_resources")
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="platform_resources",null=True
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_resources",null=True
    
    )
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True,
    related_name="group_resources")

    sender = models.ForeignKey(User, on_delete=models.CASCADE,null=True,
    related_name="sender_resources")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_resources",null=True
    )
    media_url = models.CharField(max_length=255, blank=True, null=True)
    cloud_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created_at"]
