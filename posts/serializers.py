from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    likes = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_id', 'content', 'published_at', 'parent', 'likes', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()