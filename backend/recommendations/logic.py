from django.utils import timezone
from django.db.models import Case, When, Value, FloatField
from django.core.cache import cache
from django.contrib.auth import get_user_model
from posts.models import Post
from .services import create_post_embeddings_request, retrain_user_embedding_request, get_recommended_posts_request
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

    create_post_embeddings_request(post_id, timestamp, post_content, thread_content)

def retrain_user_embedding(user_id, post_id, interaction_type):
    alpha = {
        'post': 0.15,
        'like': 0.1,
        'unlike': -0.1,
        'dislike': -0.15,
        'reply': 0.05
    }

    retrain_user_embedding_request(user_id, post_id, alpha[interaction_type])

def get_recommended_posts(user_id):
    weights = {
        'embedding_score': 0.45,
        'likes_count': 0.2,
        'comments_count': 0.1,
        'recency': 0.2,
        'followed_author': 0.05,
    }

    params = cache.get('recommendation_params') or {
        'likes_steepness': 0.05, 'likes_midpoint': 5,
        'comments_steepness': 0.1, 'comments_midpoint': 3
    }

    def sigmoid(number, steepness, midpoint):
        return 1 / (1 + np.exp(-steepness * (number - midpoint)))
    
    def calculate_score(post, score):
        return (
            weights['embedding_score'] * score +
            weights['likes_count'] * sigmoid(post.liked_by.count(), params['likes_steepness'], params['likes_midpoint']) +
            weights['comments_count'] * sigmoid(post.replies.count(), params['comments_steepness'], params['comments_midpoint']) +
            weights['recency'] * np.exp(- (timezone.now() - post.published_at).total_seconds() / (2 * 60 * 60 * 24)) +
            weights['followed_author'] * (1 if post.author_id in followed_users else 0)
        )

    scores = get_recommended_posts_request(user_id, limit=5000, delta={'days': 150})

    if not scores:
        return Post.objects.none()

    post_ids = scores.keys()

    posts = Post.objects.filter(id__in=post_ids)
    followed_users = User.objects.filter(followers__id=user_id).values_list('id', flat=True)

    case_order = Case(
        *[
            When(id=post.id, then=Value(calculate_score(post, scores[str(post.id)]))) for post in posts
        ],
        output_field=FloatField()
    )

    return posts.annotate(_order=case_order).order_by('-_order')