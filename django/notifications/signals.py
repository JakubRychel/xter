from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from posts.models import Post
from .tasks import *

User = get_user_model()

@receiver(post_save, sender=Post)
def handle_post(sender, instance, created, **kwargs):
    if created and not instance.parent:
        create_post_notifications.delay(instance.id)

@receiver(post_save, sender=Post)
def handle_reply(sender, instance, created, **kwargs):
    if created and instance.parent:
        create_reply_notification.delay(instance.id)

@receiver(m2m_changed, sender=Post.mentioned_users.through)
def handle_mention(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set: create_mention_notification.delay(instance.id, pk) 

@receiver(m2m_changed, sender=Post.liked_by.through)
def handle_(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set: create_like_notification.delay(instance.id, pk)

@receiver(m2m_changed, sender=User.followed_users.through)
def notify_user_about_new_follower(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set: create_follow_notification.delay(instance.id, pk)