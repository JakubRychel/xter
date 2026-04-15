from fastapi.concurrency import run_in_threadpool
from google.genai import types
from app.core.genai import client, MODEL
from app.schemas.genai_schema import ChatMessage

class GenAIService:
    def __init__(self):
        self.client = client

    def _map_history(self, history: list[ChatMessage]) -> list[types.Content]:
        return [
            types.Content(
                role=chunk.role,
                parts=[types.Part(text=part) for part in chunk.parts]
            ) for chunk in history
        ]

    async def generate_text(
        self,
        contents: str | list,
        system_instruction: str | None = None
    ) -> str:
        response = await run_in_threadpool(
            self.client.models.generate_content,
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            ) if system_instruction else None,
            contents=contents
        )

        return response.text
    
    async def chat(
        self,
        message: str | list,
        system_instruction: str | None = None,
        history: list[ChatMessage] | None = None,
    ) -> str:
        chat = self.client.chats.create(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            ) if system_instruction else None,
            history=self._map_history(history) if history else None,
        )

        response = await run_in_threadpool(chat.send_message, message)

        return response.text