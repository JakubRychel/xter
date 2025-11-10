from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, Event
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_seen(self, request, pk=None):
        notification = self.get_object()

        if not notification.events.filter(seen=False).exists():
            return Response({'status': 'notification_already_seen'})
        
        notification.events.update(seen=True)
        return Response({'status': 'notification_marked_as_seen'})
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_as_seen(self, request):
        unseen_events = Event.objects.filter(notification__recipient=request.user, seen=False)
        
        if not unseen_events.exists():
            return Response({'status': 'all_notifications_already_seen'})

        unseen_events.update(seen=True)
        return Response({'status': 'all_notifications_marked_as_seen'})