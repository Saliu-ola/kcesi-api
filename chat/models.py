from django.db import models
from accounts.models import User
from group.models import Group


class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_chats")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_chats")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_chats")
    organization_id = models.CharField(max_length=15, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.sender.email} --> {self.receiver.email}"

    class Meta:
        ordering = ["-created_at"]
