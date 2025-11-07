from celery import shared_task

@shared_task
def create_post_notifications(post_id):
    from posts.models import Post
    from .models import Notification

    try:
        post = Post.objects.select_related('author').prefetch_related('author__followers').get(id=post_id)
    except Post.DoesNotExist:
        return
    
    followers = post.author.followers.all()

    notifications = [
        Notification(
            related_post=post,
            recipient=follower,
            notification_type=Notification.FOLLOWED_USER_POSTED
        )
        for follower in followers
        if follower != post.author
    ]

    Notification.objects.bulk_create(notifications)

@shared_task
def create_reply_notification(post_id):
    from posts.models import Post
    from .models import Notification

    try:
        post = Post.objects.select_related('parent', 'parent__author').get(id=post_id)
    except Post.DoesNotExist:
        return
    
    Notification.objects.create(
        related_post=post,
        recipient=post.parent.author,
        notification_type=Notification.REPLY
    )

@shared_task
def create_mention_notifications(post_id, mentioned_user_ids):
    from posts.models import Post
    from .models import Notification
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    
    mentioned_users = User.objects.filter(id__in=mentioned_user_ids)

    notifications = [
        Notification(
            related_post=post,
            recipient=user,
            notification_type=Notification.MENTION
        )
        for user in mentioned_users
        if user != post.author
    ]

    Notification.objects.bulk_create(notifications)

@shared_task
def create_like_notifications(post_id, liker_user_ids):
    from posts.models import Post
    from .models import Notification
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    
    likers = User.objects.filter(id__in=liker_user_ids)

    notifications = [
        Notification(
            related_post=post,
            recipient=post.author,
            notification_type=Notification.LIKE
        )
        for liker in likers
        if liker != post.author
    ]

    Notification.objects.bulk_create(notifications)

@shared_task
def create_follow_notifications(followed_user_id, follower_user_ids):
    from .models import Notification
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        followed_user = User.objects.get(id=followed_user_id)
    except User.DoesNotExist:
        return
    
    followers = User.objects.filter(id__in=follower_user_ids)

    notifications = [
        Notification(
            recipient=followed_user,
            related_user=follower,
            notification_type=Notification.FOLLOW
        )
        for follower in followers
        if follower != followed_user
    ]

    Notification.objects.bulk_create(notifications)