from celery import shared_task
import statistics

@shared_task
def create_post_embeddings_task(post_id):
    from .logic import create_post_embeddings

    create_post_embeddings(post_id)

@shared_task
def retrain_user_embedding_task(user_id, post_id, interaction_type):
    from .logic import retrain_user_embedding

    retrain_user_embedding(user_id, post_id, interaction_type)

@shared_task
def set_recommendation_params_task():
    from django.db.models import Count
    from django.core.cache import cache
    from posts.models import Post
    
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