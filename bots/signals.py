from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from notifications.models import Notification
from .queue import push_bot_task

@receiver(post_save, sender=Notification)
def handle_notification_save(sender, instance, created, **kwargs):
    bot = instance.recipient.bot

    if not created or not bot:
        return

    def enqueue():
        payload = {
            'notification_id': instance.id,
        }

        push_bot_task(
            bot_id=bot.id,
            task_type='handle_notification',
            payload=payload,
            priority='high'
        )

    transaction.on_commit(enqueue)