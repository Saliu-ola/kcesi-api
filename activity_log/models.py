from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model

User = get_user_model()



class ActivityLog(models.Model):
    
    ACTION_CHOICES = (
        ('login_success', 'Login Successful'),
        ('login_failed_unverified', 'Login Failed Unverified'),
        ('login_failed_credentials', 'Login Failed Credentials'),
        ('reset_password', 'Reset Password'),
        ('changed_password', 'Changed Password'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs', null = True, blank = True)
    action_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank = True, related_name='performed_actions')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.content_type} - {self.date}"