from celery import shared_task
from django.db import transaction
from .utils import send_notification

@shared_task
def create_post_notifications(post_id):
    from posts.models import Post
    from .models import Notification, Event

    try:
        post = Post.objects.select_related('author').prefetch_related('author__followers').get(id=post_id)
    except Post.DoesNotExist:
        return
    
    follower_ids = post.author.followers.values_list('id', flat=True)

    notifications_to_create = [
        Notification (
            related_post_id=post.id,
            recipient_id=fid,
            notification_type=Notification.FOLLOWED_USER_POSTED
        )
        for fid in follower_ids
    ]

    Notification.objects.bulk_create(notifications_to_create, batch_size=1000, ignore_conflicts=True)

    notification_ids = Notification.objects.filter(
        related_post=post,
        notification_type=Notification.FOLLOWED_USER_POSTED,
        recipient_id__in=follower_ids
    ).values_list('id', flat=True)

    events_to_create = [
        Event(
            notification_id=nid,
            actor=post.author
        )
        for nid in notification_ids
    ]

    Event.objects.bulk_create(events_to_create, batch_size=1000)

    for notification_id in notification_ids:
        send_notification(notification_id)

@shared_task
def create_reply_notification(post_id):
    from posts.models import Post
    from .models import Notification, Event

    try:
        post = Post.objects.select_related('parent', 'parent__author').get(id=post_id)
    except Post.DoesNotExist:
        return
    
    with transaction.atomic():
        notification, created = Notification.objects.get_or_create(
            related_post=post,
            recipient=post.parent.author,
            notification_type=Notification.REPLY
        )

        Event.objects.create(notification=notification, actor=post.author)

    send_notification(notification.id)

@shared_task
def create_mention_notification(post_id, mentioned_user_id):
    from posts.models import Post
    from .models import Notification, Event

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    
    with transaction.atomic():        
        notification, created = Notification.objects.get_or_create(
            related_post=post,
            recipient_id=mentioned_user_id,
            notification_type=Notification.MENTION
        )

        Event.objects.create(notification=notification, actor=post.author)

    send_notification(notification.id)

@shared_task
def create_like_notification(post_id, liker_id):
    from posts.models import Post
    from .models import Notification, Event

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    
    with transaction.atomic():
        notification, created = Notification.objects.get_or_create(
            related_post=post,
            recipient=post.author,
            notification_type=Notification.LIKE
        )

        Event.objects.create(notification=notification, actor_id=liker_id)

    send_notification(notification.id)

@shared_task
def create_follow_notification(follower_id, followed_user_id):
    from .models import Notification, Event
    
    with transaction.atomic():
        notification, created = Notification.objects.get_or_create(
            recipient_id=followed_user_id,
            notification_type=Notification.FOLLOW
        )

        Event.objects.create(notification=notification, actor_id=follower_id)

    send_notification(notification.id)