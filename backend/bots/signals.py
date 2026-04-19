from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from notifications.models import Notification
from .queue import push_bot_task
from .models import Bot, Personality
from .tasks import create_bot_embedding_task

@receiver(post_save, sender=Notification)
def handle_notification_save(sender, instance, created, **kwargs):
    bot_id = (
        Bot.objects
        .filter(user=instance.recipient)
        .values_list('id', flat=True)
        .first()
    )

    def enqueue():
        payload = {
            'notification_id': instance.id,
        }

        push_bot_task(
            bot_id=bot_id,
            task_type='handle_notification',
            payload=payload,
            priority='high'
        )

    transaction.on_commit(enqueue)

# @receiver(post_save, sender=Personality)
# def create_bot_embedding_on_personality_change(sender, instance, created, **kwargs):
#     create_bot_embedding_task.delay(instance.bot.id)