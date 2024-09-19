from django.contrib import admin

from .models import Topic, BlogTopic, ForumTopic


class BlogTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'group', 'organization', 'created_at')
    search_fields = ('title', 'author__username', 'group__name', 'organization__name')
    list_filter = ('author', 'group', 'organization', 'created_at')
    ordering = ['-created_at']


class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'group', 'organization', 'created_at')
    search_fields = ('title', 'author__username', 'group__name', 'organization__name')
    list_filter = ('author', 'group', 'organization', 'created_at')
    ordering = ['-created_at']


admin.site.register(BlogTopic, BlogTopicAdmin)
admin.site.register(ForumTopic, ForumTopicAdmin)
admin.site.register(Topic)
