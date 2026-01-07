from fastapi import FastAPI
from app.genai.router import router as genai_router
from app.embeddings.router import router as embeddings_router

app = FastAPI(title='Xter FastAPI Service')

app.include_router(genai_router, prefix='/genai')
app.include_router(embeddings_router, prefix='/embeddings')