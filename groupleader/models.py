from django.db import models
from group.models import Group 
# Create your models here.

class GroupLeader(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="group_leaderships")
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="leader")
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} is the leader of {self.group}"

    class Meta:
        ordering = ["-assigned_at"]





class LibraryOption(models.Model):
    LIBRARY_CHOICES = [
        ('AI', 'AI Library'),
        ('FILES', 'Files Library'),
    ]

    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    library_type = models.CharField(max_length=10, choices=LIBRARY_CHOICES)

    def __str__(self):
        return f"{self.group.title} - {self.library_type}"