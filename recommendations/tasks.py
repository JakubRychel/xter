from celery import shared_task
from posts.models import Post
from .models import PostEmbedding, Interaction
from .logic import get_reply_alignment

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
    return _model

@shared_task
def register_interaction(interaction_type, post_id):
    post = Post.objects.get(id=post_id)

    try:
        post_embedding = post.embedding
    except PostEmbedding.DoesNotExist:
        model = get_embedding_model()
        embedding = model.encode(post.content)
        post_embedding = PostEmbedding.objects.create(post=post, embedding=embedding)
        post.embedding = post_embedding
        post.save()

    if interaction_type == 'like':
        label = 1
    elif interaction_type == 'unlike':
        label = 0
    elif interaction_type == 'post':
        if post.parent:
            parent = post.parent

            alignment = get_reply_alignment(parent.content, post.content)
            label = 0.5 + 0.5 * alignment['scores'][0]

        else:
            label = 1

    Interaction.objects.create(embedding=post_embedding, label=label)