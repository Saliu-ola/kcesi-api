from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
 


class Activity_flag(models.Model):

    BLOG = 1
    CHAT = 2
    FORUM = 3
    BROWSER = 4


    Activity_Choices = [

            (BLOG, 'Blog'),
            (FORUM, 'Forum'),
            (BROWSER, 'Browser'),
            (CHAT, 'Chat'),

        ]

    activity_type_id = models.PositiveSmallIntegerField(choices=Activity_Choices) 
    flagged_id = models.PositiveIntegerField() # will b d pk of (Blog, Forum ...) instance
    flagged_by = models.ForeignKey(User, on_delete=models.PROTECT) # User initiating  request
    description = models.TextField()
    datetime_flagged = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('activity_type_id', 'flagged_by', 'flagged_id')

    def __str__(self):
        return f"Flag(type={self.get_activity_type_id_display()}, by={self.flagged_by}, id={self.flagged_id})"

