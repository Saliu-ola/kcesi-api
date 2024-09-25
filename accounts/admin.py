from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import User, Token


class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    search_fields = ('email',)
    list_display = [
        'email',
        'username',
        'first_name',
        'last_name',
        'role_id',
        'organization_id',
        'organization_name',
        'is_active_for_chat',
    ]
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Personal Info'),
            {'fields': ('username', 'first_name', 'last_name', 'phone', 'role_id', 'image_url')},
        ),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        (_('Important Info'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'username',
                    'last_name',
                    'first_name',
                    'role_id',
                    'is_verified',
                    'password1',
                    'password2',
                ),
            },
        ),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Token)
