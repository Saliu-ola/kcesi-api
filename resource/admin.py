from django.contrib import admin

from .models import Resources, ResourceFileSize, ResourceDownload

class ResourceDownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'resource', 'resource_type', 'organization', 'group', 'created_at')
    search_fields = ('user__email', 'resource__title', 'organization__name', 'group__title')
    list_filter = ('user', 'resource_type', 'organization', 'group', 'created_at')
    ordering = ('-created_at',)



admin.site.register(ResourceDownload, ResourceDownloadAdmin)
admin.site.register(Resources)
admin.site.register(ResourceFileSize)
