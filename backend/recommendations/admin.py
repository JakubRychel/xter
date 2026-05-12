from django.contrib import admin
from .models import PostMetrics

@admin.register(PostMetrics)
class PostMetricsAdmin(admin.ModelAdmin):
    list_display = ('post', 'likes_count', 'replies_count', 'popularity', 'is_hot')