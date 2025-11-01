from posts.models import Post
from .logic import get_or_create_post_embedding
from celery import shared_task

@shared_task
def create_post_embedding(post_id):
    post = Post.objects.get(id=post_id)

    get_or_create_post_embedding(post)