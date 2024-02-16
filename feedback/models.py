from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from platforms.models import Platform


FEEDBACK_CONCERNED_TYPE = (
    ('ORGANIZATION', 'ORGANIZATION'),
    ('GROUP', 'GROUP'),
    ('PLATFORM', 'PLATFORM'),
)

class Feedback(models.Model):
    content = models.TextField(null=False)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_feedbacks")

    recipent_type = models.CharField(
        max_length=20, choices=FEEDBACK_CONCERNED_TYPE, null=False,
    )
    concerned_organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,null=True, related_name="organization_feedbacks"
    )
    concerned_group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, related_name="group_feedbbacks"
    )
    concerned_platform = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, related_name="platform_feedbbacks"
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"feedback--{self.pk}"

    class Meta:
        ordering = ["-created_at"]
