from django.utils import timezone
from django.db.models import Case, When
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from posts.models import Post
from .models import Interaction, PostEmbedding, UserRecommendationModel, GlobalRecommendationModel
import joblib
from datetime import timedelta


embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
sentiment_pipeline = pipeline('sentiment-analysis', model='bardsai/twitter-sentiment-pl-base')
classifier = pipeline('zero-shot-classification', model='MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli')

def get_text_embedding(text):
    embedding = embedding_model.encode(text)

    return embedding

def get_text_sentiment(text):
    sentiment = sentiment_pipeline(text)[0]

    return {
        'text': text,
        'sentiment': sentiment['label'],
        'confidence': sentiment['score']
    }

def get_reply_alignment(post, reply):
    """
    Funckja zwraca słownik 'result' gdzie w 'result.scores' jest lista trzech wartości odpowiadających etykietom
    """
    input_text = f'Post: {post}; reply: {reply}'

    result = classifier(
        input_text,
        candidate_labels=['agrees with', 'disagrees with', 'is neutral towards'],
        hypothesis_template='Reply {} the post'
    )

    return result

def register_post(user, post):
    post_embedding = post.embedding

    Interaction.objects.create(
        embedding=post_embedding,
        label=1
    )

def register_like(user, post):
    post_embedding = post.embedding

    Interaction.objects.create(
        embedding=post_embedding,
        label=1
    )

def register_unlike(user, post):
    post_embedding = post.embedding

    Interaction.objects.create(
        embedding=post_embedding,
        label=0
    )

def register_reply(user, original_post, reply_post):
    original_post_embedding = original_post.embedding

    alignment = get_reply_alignment(original_post.content, reply_post.content)

    label = 0.5 + 0.5 * alignment['scores'][0]

    Interaction.objects.create(
        embedding=original_post_embedding,
        label=label
    )

def get_recommended_posts(user):
    now = timezone.now()
    recent_posts = Post.objects.filter(published_at__gte=now - timedelta(days=3)).only('id', 'content')

    if user.is_authenticated:
        recent_posts = recent_posts.exclude(author=user)

    if not recent_posts.exists():
        return Post.objects.all().order_by('-published_at')
    
    def get_embedding(post):
        try:
            return post.embedding.embedding
        except PostEmbedding.DoesNotExist:
            embedding_obj = PostEmbedding.objects.create(post=post, embedding=get_text_embedding(post.content))
            return embedding_obj.embedding
    
    embeddings = [get_embedding(post) for post in recent_posts]

    try:
        model_obj = UserRecommendationModel.objects.get(user=user)
    except (UserRecommendationModel.DoesNotExist, Exception):
        model_obj = GlobalRecommendationModel.objects.first()
        
        if model_obj is None:
            return recent_posts.order_by('-published_at')
        
    model_path = model_obj.model.path

    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        return recent_posts.order_by('-published_at')
    
    preds = model.predict(embeddings)

    post_ids = [post.id for post in recent_posts]
    sorted_post_ids = [post_id for post_id, _ in sorted(zip(post_ids, preds), key=lambda x: x[1], reverse=True)]

    preserved_order = Case(*[
        When(pk=post_id, then=pos) for pos, post_id in enumerate(sorted_post_ids)
    ])

    return Post.objects.filter(id__in=sorted_post_ids).order_by(preserved_order)