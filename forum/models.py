from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from platforms.models import Platform
from category.models import Category
from resource.models import Resources
from django.core.validators import MinValueValidator



class Forum(models.Model):
    topic = models.CharField(max_length=225, null=True)
    content = models.TextField(null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_forums"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="cat_forums", null=True
    )
    resources = models.ManyToManyField(Resources, related_name="forums")

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_forums")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_forums")

    start_time = models.DateTimeField(null=True)

    end_time = models.DateTimeField(null=True)
    score = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=5, validators=[MinValueValidator(0.00)]
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.topic}"


    class Meta:
        ordering = ["-created_at"]




class ForumComment(models.Model):
    forum  = models.ForeignKey(
        Forum, on_delete=models.CASCADE, related_name="forum_comments"
    )
    content = models.TextField(null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_forum_comments"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_forum_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_forum_comments")
    score = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=5, validators=[MinValueValidator(0.00)]
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.user} comments"

    class Meta:
        ordering = ["-created_at"]



class CommentReplies(models.Model):
    comment = models.ForeignKey(
        ForumComment, on_delete=models.CASCADE, related_name="comment_replies"
    )
    content = models.TextField(null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_comment_replies"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="group_comment_replies"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment_replies")
    score = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=5, validators=[MinValueValidator(0.00)]
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.user} reply"

    class Meta:
        ordering = ["-created_at"]
