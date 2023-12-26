from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization


class InAppChat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_chats")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_chats")
    message = models.TextField(null=True, verbose_name="Chat contents")  
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_chats"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_chats")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.sender__email} --> {self.receiver__email}"

    class Meta:
        ordering = ["-created_at"]
