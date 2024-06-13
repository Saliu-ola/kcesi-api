from django.db import models
from group.models import Group 
from accounts.models import User
from django.utils import timezone 
# Create your models here.

class GroupLeader(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="group_leaderships")
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="leader")
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} is the leader of {self.group}"

    class Meta:
        ordering = ["-assigned_at"]



LIBRARY_CHOICES = [
        ('AI', 'AI '),
        ('FILES', 'FILES'),
    ]


class LibraryOption(models.Model):
  
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    library_type = models.CharField(max_length=10, choices=LIBRARY_CHOICES ,default='AI')

    def __str__(self):
        return f"{self.group.title} - {self.library_type}"




class LibraryFile(models.Model):

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]
     
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='library_files')
    filename = models.CharField(max_length=255)
    filedescription = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    datetime = models.DateTimeField(default=timezone.now)
    file_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.filename