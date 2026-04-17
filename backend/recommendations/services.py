from django.conf import settings
import requests

def create_post_embeddings_request(post_id, timestamp, post_content, thread_content):
    json = {
        'post_id': post_id,
        'timestamp': timestamp,
        'post_content': post_content,
        'thread_content': thread_content
    }

    print(json)

    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/posts/embed',
        json=json,
        timeout=10
    )

    response.raise_for_status()
    return response.json()

def retrain_user_embedding_request(user_id, post_id, alpha):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/users/retrain',
        json={
            'user_id': user_id,
            'post_id': post_id,
            'alpha': alpha
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()

def get_recommended_posts_request(user_id, limit=5000, delta={'days': 100}):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/recommendations/get',
        json={
            'user_id': user_id,
            'limit': limit,
            'delta': delta
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()['recommended_posts']