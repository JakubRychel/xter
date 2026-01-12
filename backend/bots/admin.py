from django.contrib import admin
from .models import Bot, Personality

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__username', 'enabled', 'mode')