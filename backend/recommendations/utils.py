from .models import PostEmbedding
from .services import embed

def get_or_create_post_embedding(post):
    try:
        post_embedding = post.embedding
    except PostEmbedding.DoesNotExist:
        post_embedding, _ = PostEmbedding.objects.get_or_create(
            post=post,
            defaults={'embedding': embed(post.content)}
        )
    
    return post_embedding.embedding