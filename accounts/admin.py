from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import User, Token


class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    search_fields = ('email',  )
    

admin.site.register(User, UserAdmin)
admin.site.register(Token)
