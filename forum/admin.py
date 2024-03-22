from django.contrib import admin

from .models import Forum,ForumComment,CommentReplies

# Register your models here.


admin.site.register(Forum)
admin.site.register(ForumComment)
admin.site.register(CommentReplies)
