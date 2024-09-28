from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from django.core.validators import MinValueValidator
from resource.models import Resources

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
    score = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=5, validators=[MinValueValidator(0.00)]
    )
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE, related_name="inappchat_resource", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.sender} --> {self.receiver}"

    class Meta:
        ordering = ["-created_at"]
