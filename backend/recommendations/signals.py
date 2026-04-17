from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from posts.models import Post
from .tasks import create_post_embeddings_task, retrain_user_embedding_task

@receiver(post_save, sender=Post)
def create_post_embeddings_on_save(sender, instance, created, **kwargs):
    create_post_embeddings_task.delay(instance.id)

@receiver(post_save, sender=Post)
def retrain_user_embedding_on_post(sender, instance, created, **kwargs):
    if not instance.parent:
        retrain_user_embedding_task.delay(instance.author_id, instance.id, 'post')

@receiver(post_save, sender=Post)
def retrain_user_embedding_on_reply(sender, instance, created, **kwargs):
    if created and instance.parent:
        retrain_user_embedding_task.delay(instance.author_id, instance.parent.id, 'reply')

@receiver(m2m_changed, sender=Post.liked_by.through)
def retrain_user_embedding_on_like(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            retrain_user_embedding_task.delay(user_id, instance.id, 'like')

@receiver(m2m_changed, sender=Post.liked_by.through)
def retrain_user_embedding_on_unlike(sender, instance, action, pk_set, **kwargs):
    if action == 'post_remove':
        for user_id in pk_set:
            retrain_user_embedding_task.delay(user_id, instance.id, 'unlike')

@receiver(m2m_changed, sender=Post.disliked_by.through)
def retrain_user_embedding_on_dislike(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            retrain_user_embedding_task.delay(user_id, instance.id, 'dislike')
