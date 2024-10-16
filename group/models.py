from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.

"""
class Group:
    id int
    title str(50)
    content text
    created datetime
"""

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    organization_id = models.CharField(max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    related_terms = models.JSONField(null=True, blank=True)
    related_terms_library_b = models.JSONField(null=True, blank=True)           #from files upload

    def __str__(self) -> str:
        return self.title or " "

    class Meta:
        ordering = ["-created_at"]


class UserGroup(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="user_groups",
        null=True,
    )
    groups = models.ManyToManyField("group.Group")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.user}"

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=['user'], name='unique_user_per_group')]




