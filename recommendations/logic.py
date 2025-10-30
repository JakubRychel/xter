from django.utils import timezone
from django.db.models import Case, When, IntegerField
from sentence_transformers import SentenceTransformer
from posts.models import Post
from .models import PostEmbedding, GlobalEmbedding, UserEmbedding
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

    try:
        post_embedding = post.embedding
    except PostEmbedding.DoesNotExist:
        embedding = embedding_model.encode(post.content)
        post_embedding = PostEmbedding.objects.create(post=post, embedding=embedding)
        post.embedding = post_embedding
        post.save()

    user_vector = np.array(user_embedding.embedding, dtype='float32')
    post_vector = np.array(post_embedding.embedding, dtype='float32')

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

def get_initial_recommended_posts(user):
    user_embedding = get_user_embedding(user)

    now = timezone.now()
    recent_posts = (
        Post.objects.filter(published_at__gte=now - timedelta(days=100))
        .select_related('embedding')
        .only('id', 'published_at', 'embedding__embedding')
    ) 

    post_ids = []
    embeddings = []

    for post in recent_posts:
        try:
            post_embedding = post.embedding
        except PostEmbedding.DoesNotExist:
            post_embedding = PostEmbedding.objects.create(post=post, embedding=embedding_model.encode(post.content))
            post.embedding = post_embedding
            post.save()

        post_ids.append(post.id)
        embeddings.append(post_embedding.embedding)

    embeddings = np.array(embeddings, dtype='float32')

    d = 512

    index = faiss.IndexFlatIP(d)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    faiss_id_to_post_id = {faiss_id: post_id for faiss_id, post_id in enumerate(post_ids)}

    user_embedding = np.array([user_embedding], dtype='float32')
    faiss.normalize_L2(user_embedding)

    D, I = index.search(user_embedding, k=200) #D - odległość, I - posortowane indeksy

    recommended_post_ids = [faiss_id_to_post_id[i] for i in I[0]]

    recommended_posts = (
        Post.objects.filter(id__in=recommended_post_ids)
        .annotate(
            _order=Case(
                *[When(id=int(post_id), then=pos) for pos, post_id in enumerate(recommended_post_ids)],
                output_field=IntegerField()
            )
        )
        .order_by('_order')
    )

    return recommended_posts