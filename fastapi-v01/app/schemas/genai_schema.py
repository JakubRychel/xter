from pydantic import BaseModel
from typing import List, Literal, Union

class ChatMessage(BaseModel):
    role: Literal['user', 'model']
    parts: List[str]

class ChatRequest(BaseModel):
    message: Union[str, List[str]]
    system_instruction: str
    history: List[ChatMessage]

class GenerateTextRequest(BaseModel):
    contents: Union[str, List[str]]
    system_instruction: str

class TextResponse(BaseModel):
    text: str