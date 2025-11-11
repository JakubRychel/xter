from rest_framework.serializers import ModelSerializer
from .models import Notification, Event
from posts.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'displayed_name']

class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content']

class EventSerializer(ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'actor', 'seen', 'created_at']

class NotificationSerializer(ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    related_post = PostSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'related_post', 'events']
