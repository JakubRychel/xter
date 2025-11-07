from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_seen(self, request, pk=None):
        notification = self.get_object()
        
        if notification.seen:
            return Response({'status': 'already_seen'})
        
        self.get_queryset().filter(pk=notification.pk, seen=False).update(seen=True)

        return Response({'status': 'marked_as_seen'})