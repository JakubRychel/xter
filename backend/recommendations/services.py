from django.conf import settings
from common.http_client import post

async def create_post_embeddings_request(post_id, timestamp, post_content, thread_content):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/posts/embed',
        json={
            'post_id': post_id,
            'timestamp': timestamp,
            'post_content': post_content,
            'thread_content': thread_content
        }
    )

    return data

async def retrain_user_embedding_request(user_id, post_id, alpha):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/users/retrain',
        json={
            'user_id': user_id,
            'post_id': post_id,
            'alpha': alpha
        }
    )

    return data

async def get_recommended_posts_request(user_id, limit=5000, delta={'days': 100}):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/recommendations/get',
        json={
            'user_id': user_id,
            'limit': limit,
            'delta': delta
        }
    )

    return data['recommended_posts']

async def get_post_score_request(user_id, post_id):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/recommendations/score',
        json={
            'user_id': user_id,
            'post_id': post_id
        }
    )

    return data['score']