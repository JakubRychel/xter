from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post

@receiver(m2m_changed, sender=Post.liked_by.through)
def mark_post_as_readed_on_like(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        instance.read_by.add(*pk_set)