from django.conf import settings
import requests

def embed(text):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/embed',
        json={'text': text},
        timeout=10
    )

    response.raise_for_status()
    return response.json()['embedding']

def get_nearest_neighbors(query_vector, vectors, k=200, d=512):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/get-nearest-neighbors',
        json={
            'query_vector': query_vector,
            'vectors': vectors,
            'k': k,
            'd': d
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()['result']

