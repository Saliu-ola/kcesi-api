from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from platforms.models import Platform
from blog.models import Blog
from forum.models import Forum

class Topic(models.Model):
    name = models.CharField(max_length=225, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_topics")
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="platform_topics")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_topics"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_topics")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-created_at"]



class BlogTopic(models.Model):
    title = models.CharField(max_length=200)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='topics', null = True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='blog_topics', blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='blog_topics', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_topics')

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class ForumTopic(models.Model):
    title = models.CharField(max_length=200)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='topics', null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='forum_topics', blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='forum_topics', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]