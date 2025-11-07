from django.db import models

class Notification(models.Model):
    REPLY = 'reply'
    LIKE = 'like'
    FOLLOW = 'follow'
    MENTION = 'mention'
    FOLLOWED_USER_POSTED = 'followed_user_posted'
    SYSTEM = 'system'
    OTHER = 'other'

    NOTIFICATION_TYPES = [
        (REPLY, 'Someone replied to your post'),
        (LIKE, 'Someone liked your post'),
        (FOLLOW, 'Someone has followed you'),
        (MENTION, 'Someone mentioned you'),
        (FOLLOWED_USER_POSTED, 'Someone you follow created a post'),
        (SYSTEM, 'System notification'),
        (OTHER, 'Other'),
    ]

    notification_type = models.CharField(choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey('users.User', related_name='notifications', on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    related_post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, null=True, blank=True)
    related_user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)