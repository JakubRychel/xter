from app.schemas.genai_schema import ChatMessage

class GenAIService:
    def __init__(self):
        pass

    async def generate_text(
        self,
        contents: str | list,
        system_instruction: str | None = None
    ) -> str:
        print('received')

    async def chat(
        self,
        message: str | list,
        system_instruction: str | None = None,
        history: list[ChatMessage] | None = None
    ) -> str:
        print('received')