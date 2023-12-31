from pickle import TRUE

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

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created_at"]
