from django.conf import settings
import requests

def generate_text(system_instruction, contents):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/genai/generate-text',
        json={'system_instruction': system_instruction, 'contents': contents},
        timeout=10
    )

    response.raise_for_status()
    return response.json()['text']

def chat(system_instruction, history, message):
    response = requests.post(
        f'{settings.FASTAPI_SERVICES_URL}/genai/chat',
        json={
            'system_instruction': system_instruction,
            'history': history,
            'message': message
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()['text']