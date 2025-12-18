from django.db.models import OuterRef, Subquery
from django.db.models.fields import DateTimeField
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Notification, Event
from .serializers import NotificationSerializer

class NotificationPagePagination(PageNumberPagination):
    page_size = 10

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagePagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        latest_event_subquery = Event.objects.filter(
            notification_id=OuterRef('pk')
        ).order_by('-created_at').values('created_at')[:1]

        return (
            super().get_queryset()
            .filter(recipient=self.request.user)
            .annotate(
                latest_event_created_at=Subquery(latest_event_subquery, output_field=DateTimeField())
            )
            .prefetch_related('events__actor', 'related_post')
            .order_by('-latest_event_created_at')
        )

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