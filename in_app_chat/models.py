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
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, related_name="group_chats"
    )
    content_type = models.CharField(max_length=255, null=True)
    unique_identifier = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


    def save(self, *args, **kwargs):
        if self.message and not self.message.endswith(" correct"):
            self.message = self.message + " correct"
        super(InAppChat, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.sender} --> {self.receiver}"

    class Meta:
        ordering = ["-created_at"]
