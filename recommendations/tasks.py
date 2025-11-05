from django.db.models import Count
from django.core.cache import cache
from posts.models import Post
from .logic import get_or_create_post_embedding
from celery import shared_task
import statistics

@shared_task
def create_post_embedding(post_id):
    post = Post.objects.get(id=post_id)

    get_or_create_post_embedding(post)

@shared_task
def set_recommendation_params():
    posts = (
        Post.objects
        .annotate(likes_count=Count('liked_by'), replies_count=Count('replies'))
        .order_by('-created_at')[:5000]
    )

    likes_counts = list(posts.values_list('likes_count', flat=True))
    replies_counts = list(posts.values_list('replies_count', flat=True))

    if likes_counts:
        median_likes = statistics.median(likes_counts)
    else:
        median_likes = 0

    if replies_counts:
        median_replies = statistics.median(replies_counts)
    else:
        median_replies = 0

    cache.set('recommendation_params', {
        'likes_steepness': 0.1,
        'likes_midpoint': median_likes,
        'comments_steepness': 0.2,
        'comments_midpoint': median_replies,
    }, None)