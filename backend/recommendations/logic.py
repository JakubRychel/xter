from asgiref.sync import sync_to_async
from itertools import chain

from datetime import datetime, timezone
from django.db.models import Case, When
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from posts.models import Post
from .models import PostMetrics
from .services import create_post_embeddings_request, retrain_user_embedding_request, get_recommended_posts_request, get_post_scores_request
import numpy as np

User = get_user_model()

# def stringify_posts(*posts):
#     return '\n\n'.join([
#         f'''
#         Autor: {post.author.displayed_name} (@{post.author.username})
#         Data publikacji: {post.published_at.strftime('%d %b %Y, %H:%M')}
#         Treść: {post.content}
#         ''' for post in posts
#     ])

def collect_thread(post_id):
    post_ids = []
    current_id = post_id

    while current_id:
        post_ids.append(current_id)

        parent_id = (
            Post.objects
            .filter(id=current_id)
            .values_list('parent_id', flat=True)
            .first()
        )

        current_id = parent_id

    order = Case(
        *[When(id=id, then=pos) for pos, id in enumerate(reversed(post_ids))]
    )

    posts = (
        Post.objects
        .filter(id__in=post_ids)
        .order_by(order)
    )

    return posts

def create_post_embeddings(post_id):
    post = Post.objects.filter(id=post_id).only('content', 'published_at').first()

    post_content = post.content
    timestamp = int(post.published_at.timestamp())

    thread = collect_thread(post_id)
    thread_content = '\n\n'.join(thread.values_list('content', flat=True))

    response = create_post_embeddings_request(post_id, timestamp, post_content, thread_content)

    if response.get('status') == 'ok':
        Post.objects.filter(id=post_id).update(embeddings_created=True)

def retrain_user_embedding(user_id, post_id, interaction_type):
    alpha = {
        'post': 0.15,
        'like': 0.1,
        'unlike': -0.1,
        'dislike': -0.15,
        'reply': 0.05
    }

    retrain_user_embedding_request(user_id, post_id, alpha[interaction_type])

async def rerank_posts(scored_posts, user_id):
    weights = {
        'embedding_score': 0.45,
        'likes_count': 0.2,
        'replies_count': 0.1,
        'recency': 0.2,
        'followed_author': 0.05,
        'read_by_user': 1
    }

    params = cache.get('recommendation_params') or {
        'likes_steepness': 0.05, 'likes_midpoint': 5,
        'replies_steepness': 0.1, 'replies_midpoint': 3
    }

    def sigmoid(number, steepness, midpoint):
        return float(1 / (1 + np.exp(-steepness * (number - midpoint))))

    scored_posts = {
        int(post_id): score for post_id, score in scored_posts.items()
    }

    post_ids = scored_posts.keys()

    posts = await sync_to_async(list)(
        Post.objects
        .filter(id__in=post_ids)
        .annotate(read_by_ids=ArrayAgg('read_by__id', default=[]))
        .values('id', 'author_id', 'published_at', 'likes_count', 'replies_count', 'read_by_ids')
    )

    followed_users = await sync_to_async(set)(User.objects.filter(id=user_id).values_list('id', flat=True))

    now = datetime.now(timezone.utc)

    def calculate_score(post, score):
        embedding_score = (score + 1) / 2
        likes_count = sigmoid(post['likes_count'], params['likes_steepness'], params['likes_midpoint'])
        replies_count = sigmoid(post['replies_count'], params['replies_steepness'], params['replies_midpoint'])
        recency = float(np.exp(- (now - post['published_at']).total_seconds() / (2 * 60 * 60 * 24)))
        followed_author = 1 if post['author_id'] in followed_users else 0
        read_by_user = 0 if user_id in post['read_by_ids'] else 1

        score = (
            weights['embedding_score'] * embedding_score +
            weights['likes_count'] * likes_count +
            weights['replies_count'] * replies_count +
            weights['recency'] * recency +
            weights['followed_author'] * followed_author +
            weights['read_by_user'] * read_by_user
        )

        return score
    
    reranked_posts = {post['id']: calculate_score(post, scored_posts[post['id']]) for post in posts}

    return reranked_posts

def get_popular_post_ids(limit: int = 1000):
    post_ids = PostMetrics.objects.order_by('-popularity').values_list('post_id', flat=True)[:limit]

    return post_ids

async def get_recommendations(user_id: int) -> dict[int, float]:
    chunks = [{
        'limit': 4000,
        'time_range': {'end': {'days': 7 }}
    }, {
        'limit': 800,
        'time_range': {'start': {'days': 7 }, 'end': {'days': 30 }}
    }, {
        'limit': 200,
        'time_range': {'start': {'days': 30 }}
    }]

    scored_recommended_posts = await get_recommended_posts_request(user_id, chunks=chunks)

    popular_post_ids = await sync_to_async(list)(get_popular_post_ids())

    scored_popular_posts = await get_post_scores_request(user_id, popular_post_ids)

    posts = scored_recommended_posts | scored_popular_posts

    if not posts:
        return {}

    reranked_posts = await rerank_posts(posts, user_id)

    return reranked_posts

async def refill_recommendations(user_id: int, limit: int = 25, timestamp: int = None) -> dict[int, float]:
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)

    seconds = int((now - dt).total_seconds())

    chunks = [{
        'limit': limit,
        'time_range': {'end': {'seconds': seconds }}
    }]

    scored_posts = await get_recommended_posts_request(user_id, chunks=chunks)

    if not scored_posts:
        return {}

    reranked_posts = await rerank_posts(scored_posts, user_id)

    return reranked_posts