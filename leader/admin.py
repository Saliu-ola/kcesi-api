from django.contrib import admin

from .models import Socialization, Internalization, Externalization, Combination

# Register your models here.

admin.site.register(Socialization)
admin.site.register(Externalization)
admin.site.register(Internalization)
admin.site.register(Combination)
