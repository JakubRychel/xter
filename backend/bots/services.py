from django.conf import settings
from common.http_client import post

async def generate_text_request(system_instruction, contents):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/genai/generate-text',
        json={
            'system_instruction': system_instruction,
            'contents': contents
        }
    )

    return data['text']

async def chat_request(system_instruction, history, message):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/genai/chat',
        json={
            'system_instruction': system_instruction,
            'history': history,
            'message': message
        }
    )

    return data['text']

async def create_bot_embedding_request(bot_id, personality):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/embeddings/bots/embed',
        json={
            'bot_id': bot_id,
            'bot_personality': personality
        }
    )

    return data

async def score_thread_request(bot_id, post_id):
    data = await post(
        f'{settings.FASTAPI_SERVICES_URL}/recommendations/score',
        json={
            'bot_id': bot_id,
            'post_id': post_id
        }
    )

    return data['score']