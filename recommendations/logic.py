from django.utils import timezone
from django.db.models import Case, When, Value, FloatField
from django.core.cache import cache
from sentence_transformers import SentenceTransformer
from posts.models import Post
from .models import GlobalEmbedding, UserEmbedding
from .utils import get_or_create_post_embedding
from datetime import timedelta
import faiss
import numpy as np

embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

def retrain_user_embedding(user, interaction_type, post_id):
    try:
        user_embedding = user.embedding
    except Exception:
        try:
            global_embedding = GlobalEmbedding.objects.first()
            user_embedding = user.embedding = UserEmbedding.objects.create(user=user, embedding=global_embedding.embedding)
        except Exception:
            user_embedding = user.embedding = UserEmbedding.objects.create(user=user, embedding=[0.0] * 512)
        user_embedding.save()

    post = Post.objects.get(id=post_id)

    post_embedding = get_or_create_post_embedding(post)

    user_vector = np.array(user_embedding.embedding, dtype='float32')
    post_vector = np.array(post_embedding, dtype='float32')

    alpha = {
        'post': 0.15,
        'like': 0.1,
        'unlike': -0.1,
        'dislike': -0.15,
        'reply': 0.05
    }

    user_vector = user_vector + alpha[interaction_type] * (post_vector - user_vector)

    user.embedding.embedding = user_vector.tolist()
    user.embedding.save()
    
def get_user_embedding(user):
    try:
        return user.embedding.embedding
    except Exception:
        return [0.0] * 512

def get_initial_recommended_post_ids(user):
    user_embedding = get_user_embedding(user)

    now = timezone.now()
    recent_posts = (
        Post.objects
        .filter(published_at__gte=now - timedelta(days=100))
        .select_related('embedding')
        .only('id', 'published_at', 'embedding__embedding')
    )

    post_ids = []
    embeddings = []

    for post in recent_posts:
        post_embedding = get_or_create_post_embedding(post)

        post_ids.append(post.id)
        embeddings.append(post_embedding)

    embeddings = np.array(embeddings, dtype='float32')

    d = 512

    index = faiss.IndexFlatIP(d)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    faiss_id_to_post_id = {faiss_id: post_id for faiss_id, post_id in enumerate(post_ids)}

    user_embedding = np.array([user_embedding], dtype='float32')
    faiss.normalize_L2(user_embedding)

    D, I = index.search(user_embedding, k=200) # D - odległość, I - indeksy

    return (
        [faiss_id_to_post_id[i] for i in I[0]],
        {faiss_id_to_post_id[i]: D[0][n] for n, i in enumerate(I[0])}
    )

def sigmoid(number, steepness, midpoint):
    return 1 / (1 + np.exp(-steepness * (number - midpoint)))

def get_recommended_posts(user):
    weights = {
        'embedding_distance': 0.45,
        'likes_count': 0.2,
        'comments_count': 0.1,
        'recency': 0.2,
        'followed_author': 0.05,
    }

    params = cache.get('recommendation_params') or {
        'likes_steepness': 0.05, 'likes_midpoint': 5,
        'comments_steepness': 0.1, 'comments_midpoint': 3
    }

    def calculate_score(post, distance):
        return (
            weights['embedding_distance'] * (1 - distance) +
            weights['likes_count'] * sigmoid(post.liked_by.count(), params['likes_steepness'], params['likes_midpoint']) +
            weights['comments_count'] * sigmoid(post.replies.count(), params['comments_steepness'], params['comments_midpoint']) +
            weights['recency'] * np.exp(- (timezone.now() - post.published_at).total_seconds() / (2 * 60 * 60 * 24)) +
            weights['followed_author'] * (1 if post.author_id in followed_users else 0)
        )

    post_ids, distances = get_initial_recommended_post_ids(user)
    posts = Post.objects.filter(id__in=post_ids)

    followed_users = set(user.followed_users.values_list('id', flat=True))

    case_order = Case(
        *[
            When(id=post.id, then=Value(calculate_score(post, distances[post.id]))) for post in posts
        ],
        output_field=FloatField()
    )

    return posts.annotate(_order=case_order).order_by('-_order')