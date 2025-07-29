from rest_framework import serializers
from .models import Post


class BasePostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')

    likes = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    likes_count = serializers.SerializerMethodField()

    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_id', 'content', 'published_at', 'likes', 'likes_count', 'replies_count']

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_replies_count(self, obj):
        return obj.replies.count()
    
class ParentSerializer(BasePostSerializer):
    class Meta(BasePostSerializer.Meta):
        fields = ['id', 'author', 'content', 'published_at']

class PostSerializer(BasePostSerializer):
    replies = BasePostSerializer(read_only=True, many=True)
    parent = ParentSerializer(read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(source='parent', queryset=Post.objects.all(), write_only=True, required=False)

    class Meta(BasePostSerializer.Meta):
        fields = BasePostSerializer.Meta.fields + ['parent', 'parent_id', 'replies']