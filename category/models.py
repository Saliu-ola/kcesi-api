from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization


class Category(models.Model):
    name = models.CharField(max_length=225, null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_categories"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_categories")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_categories")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.topic

    class Meta:
        ordering = ["-created_at"]
