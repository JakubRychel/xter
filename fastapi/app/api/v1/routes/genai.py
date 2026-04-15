from fastapi import APIRouter, Depends
from app.schemas.genai_schema import GenerateTextRequest, ChatRequest, TextResponse
from app.services.genai_service import GenAIService

router = APIRouter(prefix='/genai', tags=['genai'])

@router.post('/generate-text', response_model=TextResponse)
async def generate_text(
    payload: GenerateTextRequest,
    service: GenAIService = Depends()
):
    generated_text = await service.generate_text(
        payload.contents,
        payload.system_instruction
    )

    return {'text': generated_text}

@router.post('/chat', response_model=TextResponse)
async def chat(
    payload: ChatRequest,
    service: GenAIService = Depends()
):
    chat_response = await service.chat(
        payload.message,
        payload.system_instruction,
        payload.history
    )

    return {'text': chat_response}