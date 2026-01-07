from django.db import models
from django.contrib.auth import get_user_model
from pgvector.django import VectorField

User = get_user_model()

class Personality(models.Model):
    description = models.TextField(blank=True, null=True)
    embedding = VectorField(dimensions=512, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from .tasks import generate_personality_embedding
        generate_personality_embedding.delay(self.id)

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