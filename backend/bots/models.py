from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction
from .tasks import plan_next_task, create_bot_embedding_task

User = get_user_model()

class Personality(models.Model):
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_description = Personality.objects.only('description').get(pk=self.pk).description

        else:
            old_description = None

        super().save(*args, **kwargs)

        if old_description != self.description:
            transaction.on_commit(lambda: create_bot_embedding_task.delay(self.bot.id))

class Bot(models.Model):
    ACTIVE = 'active'
    STANDBY = 'standby'
    INACTIVE = 'inactive'

    MODES = [
        (ACTIVE, 'Active'),
        (STANDBY, 'Standby'),
        (INACTIVE, 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bot')
    personality_obj = models.OneToOneField(Personality, on_delete=models.CASCADE, related_name='bot', blank=True, null=True)

    enabled = models.BooleanField(default=False)
    mode = models.CharField(choices=MODES, default=ACTIVE)

    @property
    def personality(self):
        if self.personality_obj:
            return self.personality_obj.description
        return None
    
    def save(self, *args, **kwargs):
        if self.pk:
            old = Bot.objects.get(pk=self.pk)
            was_enabled = old.enabled

        else:
            was_enabled = False

        super().save(*args, **kwargs)

        if not was_enabled and self.enabled:
            transaction.on_commit(lambda: plan_next_task(self.id))