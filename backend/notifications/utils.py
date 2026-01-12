from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import NotificationSerializer
from .models import Notification

def send_notification(notification_id):
    notification = Notification.objects.get(id=notification_id)
    serializer = NotificationSerializer(notification)

    channel_layer = get_channel_layer()
    group_name = f'user_{notification.recipient.id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'notification': serializer.data
        }
    )