from django.contrib import admin

from .models import Comment, Blog,BlogCommentReplies

# Register your models here.


admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(BlogCommentReplies)
