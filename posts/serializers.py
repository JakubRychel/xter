from rest_framework import serializers
from .models import Post

class BasePostSerializer(serializers.ModelSerializer):
    author_id = serializers.ReadOnlyField(source='author.id')
    author_username = serializers.ReadOnlyField(source='author.username')
    author_displayed_name = serializers.ReadOnlyField(source='author.displayed_name')

    published_at = serializers.DateTimeField(format='%d %b %Y, %H:%M', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author_id', 'author_username', 'author_displayed_name', 'content', 'published_at']

class PostSerializer(BasePostSerializer):
    likes = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    likes_count = serializers.SerializerMethodField()

    replies_count = serializers.SerializerMethodField()

    parent_id = serializers.PrimaryKeyRelatedField(source='parent', queryset=Post.objects.all(), write_only=True, required=False, allow_null=True)
    parent = BasePostSerializer(read_only=True)

    class Meta(BasePostSerializer.Meta):
        model = Post
        fields = BasePostSerializer.Meta.fields + ['likes', 'likes_count', 'replies_count', 'parent_id', 'parent']

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_replies_count(self, obj):
        return obj.replies.count()

