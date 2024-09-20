from django.contrib import admin

from .models import Comment, Blog,BlogCommentReplies, BlogRead

class BlogReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'group', 'organization', 'created_at')
    search_fields = ('user__email', 'blog__topic', 'group__title', 'organization__name')
    list_filter = ('user', 'group', 'organization', 'created_at')
    ordering = ('-created_at',)


admin.site.register(BlogRead, BlogReadAdmin)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(BlogCommentReplies)
