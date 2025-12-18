from sentence_transformers import SentenceTransformer
from django.db import transaction, IntegrityError
from .models import PostEmbedding

def get_text_embedding(text):
    embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
    embedding = embedding_model.encode(text)

    return embedding

def get_or_create_post_embedding(post):
    try:
        post_embedding = post.embedding
    except PostEmbedding.DoesNotExist:
        try:
            with transaction.atomic():
                post_embedding = PostEmbedding.objects.create(post=post, embedding=get_text_embedding(post.content))
        except IntegrityError:
            post_embedding = post.embedding
    
    return post_embedding.embedding