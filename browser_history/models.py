from django.db import models
from accounts.models import User
from group.models import Group
from organization.models import Organization
from platforms.models import Platform


class BrowserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_browser_histories")
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="group_browser_histories"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="organization_browser_histories"
    )

    url = models.CharField(max_length=225, null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    time_spent = models.IntegerField(null=True)
    date_time = models.DateTimeField(auto_now=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self) -> str:
        return f"{self.user}: {self.url}" or " "

    class Meta:
        ordering = ["-created_at"]
