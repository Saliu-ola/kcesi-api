from django.contrib import admin

from .models import Forum, ForumComment, CommentReplies, ForumRead

class ForumReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'forum', 'group', 'organization', 'created_at')
    search_fields = ('user__email', 'forum__topic', 'group__title', 'organization__name')
    list_filter = ('user' ,'group', 'organization', 'created_at')
  
  

admin.site.register(ForumRead, ForumReadAdmin)
admin.site.register(Forum)
admin.site.register(ForumComment)
admin.site.register(CommentReplies)
