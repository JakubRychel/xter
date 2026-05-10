from django.conf import settings
import requests
from common.http_client import post

def generate_text_request(system_instruction, contents):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/genai/generate-text',
        json={
            'system_instruction': system_instruction,
            'contents': contents
        },
        timeout=10
    )

    return response.json()['text']

def chat_request(system_instruction, history, message):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/genai/chat',
        json={
            'system_instruction': system_instruction,
            'history': history,
            'message': message
        },
        timeout=10
    )

    return response.json()['text']

def create_bot_embedding_request(bot_id, personality):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/bots/embed',
        json={
            'bot_id': bot_id,
            'bot_personality': personality
        },
        timeout=10
    )

    return response.json()

def score_thread_request(bot_id, post_id):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/recommendations/score',
        json={
            'bot_id': bot_id,
            'post_id': post_id
        },
        timeout=10
    )

    return response.json()['score']