from fastapi import APIRouter
from app.genai.services import generate_text, chat
from app.genai.schemas import GenerateTextRequest, ChatRequest, TextResponse

router = APIRouter(tags=['genai'])

@router.post('/generate-text', response_model=TextResponse)
def generate_text_endpoint(payload: GenerateTextRequest):
    text = generate_text(
        system_instruction=payload.system_instruction,
        contents=payload.contents
    )

    return {'text': text}

@router.post('/chat', response_model=TextResponse)
def chat_endpoint(payload: ChatRequest):
    text = chat(
        system_instruction=payload.system_instruction,
        history=payload.history,
        message=payload.message
    )

    return {'text': text}