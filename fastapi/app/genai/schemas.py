from pydantic import BaseModel
from typing import List, Literal, Union

class ChatMessage(BaseModel):
    role: Literal['user', 'model']
    contents: List[str]

class ChatRequest(BaseModel):
    system_instruction: str
    history: List[ChatMessage]
    message: str

class GenerateTextRequest(BaseModel):
    system_instruction: str
    contents: Union[str, List[str]]

class TextResponse(BaseModel):
    text: str