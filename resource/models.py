from django.db import models
from platforms.models import Platform
from organization.models import Organization
from group.models import Group
from accounts.models import User


class Type(models.Model):
    name = models.CharField(max_length=50, null=True)

    def __str__(self) -> str:
        return self.name


class Resources(models.Model):
    title = models.CharField(max_length=50, null=True)
    size = models.IntegerField(null=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name="type_resources")
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="platform_resources"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_resources"
    )
    group = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="group_resources"
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_resources")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_resources")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created_at"]
