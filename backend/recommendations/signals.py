from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post
from .tasks import create_post_embedding

@receiver(post_save, sender=Post)
def create_post_embedding_on_save(sender, instance, created, **kwargs):
    create_post_embedding.delay(instance.id)