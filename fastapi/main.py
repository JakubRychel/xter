from fastapi import FastAPI
from genai.router import router as genai_router
from embeddings.router import router as embeddings_router

app = FastAPI(title='Xter FastAPI Service')

app.include_router(genai_router, prefix='/genai')
app.include_router(embeddings_router, prefix='/embeddings')