from google import genai
from google.genai import types

client = genai.Client()

MODEL = 'gemini-2.5-flash-lite'

def generate_text(system_instruction, contents):
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        contents=contents
    )

    return response.text

def chat(system_instruction, history, message):
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
        history=[types.Content(
            role=chunk.role,
            parts=[types.Part(text=part) for part in chunk.parts]
        ) for chunk in history]
    )

    response = chat.send_message(message)

    return response.text