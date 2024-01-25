from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from platforms.models import Platform
from category.models import Category


class Forum(models.Model):
    topic = models.CharField(max_length=225, null=True)
    content = models.TextField(null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_forums"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="cat_forums", null=True
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_forums")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_forums")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.topic

    class Meta:
        ordering = ["-created_at"]
