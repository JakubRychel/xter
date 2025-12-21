from django.db import transaction, IntegrityError
from .models import PostEmbedding
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

def get_text_embedding(text):
    return embedding_model.encode(text)

def get_or_create_post_embedding(post):
    try:
        post_embedding = post.embedding
    except PostEmbedding.DoesNotExist:
        post_embedding, _ = PostEmbedding.objects.get_or_create(
            post=post,
            defaults={'embedding': get_text_embedding(post.content)}
        )
    
    return post_embedding.embedding