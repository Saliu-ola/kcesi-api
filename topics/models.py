from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from platforms.models import Platform


class Topic(models.Model):
    name = models.CharField(max_length=225, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_topics")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="platform_topics")
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_topics"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_topics")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-created_at"]
