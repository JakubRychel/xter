from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from posts.models import Post
from .tasks import *

User = get_user_model()

@receiver(post_save, sender=Post)
def notify_followers_about_post(sender, instance, created, **kwargs):
    if created and not instance.parent:
        create_post_notifications.delay(instance.id)

@receiver(post_save, sender=Post)
def notify_parent_author_about_reply(sender, instance, created, **kwargs):
    if created and instance.parent:
        create_reply_notification.delay(instance.id)

@receiver(m2m_changed, sender=Post.mentioned_users.through)
def notify_about_mention(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        create_mention_notifications.delay(instance.id, list(pk_set))

@receiver(m2m_changed, sender=Post.liked_by.through)
def notify_post_author_about_like(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        create_like_notifications.delay(instance.id, list(pk_set))

@receiver(m2m_changed, sender=User.followed_users.through)
def notify_user_about_new_follower(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        create_follow_notifications.delay(instance.id, list(pk_set))