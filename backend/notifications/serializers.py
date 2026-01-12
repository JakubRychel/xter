from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Notification
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

class NotificationSerializer(ModelSerializer):
    related_post = PostSerializer(read_only=True)

    latest_actors = SerializerMethodField()
    events_count = SerializerMethodField()
    seen = SerializerMethodField()
    updated_at = SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'related_post', 'latest_actors', 'events_count', 'seen', 'updated_at']

    def get_latest_actors(self, obj):
        latest_events = obj.events.all().order_by('-created_at')[:3]
        return UserSerializer([event.actor for event in latest_events], many=True).data

    def get_events_count(self, obj):
        return obj.events.count()
    
    def get_seen(self, obj):
        return not obj.events.filter(seen=False).exists()
    
    def get_updated_at(self, obj):
        try:
            latest_event = obj.events.latest('created_at')
        except Notification.events.RelatedObjectDoesNotExist:
            return None

        return latest_event.created_at.isoformat() if latest_event else None