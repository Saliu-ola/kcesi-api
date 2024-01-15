from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from platforms.models import Platform
from resource.models import Resources
from category.models import Category


class Blog(models.Model):
    topic = models.CharField(max_length=225, null=True)
    content = models.TextField(null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_blogs"
    )
    category = models.ForeignKey(
        Category, on_delete=models.DO_NOTHING, null=True
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_blogs")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_blogs")
    resources = models.ManyToManyField(Resources, null=True, related_name="blogs")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.topic

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    blog = organization = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="blog_comments"
    )
    content = models.TextField(null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.DO_NOTHING, related_name="organization_comments"
    )
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, related_name="group_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")

    Platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="platform_comments"
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.user} comments"

    class Meta:
        ordering = ["-created_at"]
