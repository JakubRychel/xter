from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import router
from app.core.qdrant import qdrant_client
from app.core.config import settings
from qdrant_client.models import VectorParams, Distance


async def ensure_qdrant_collections(qdrant, vector_size: int):
    if not await qdrant.collection_exists('posts'):
        qdrant.create_collection(
            collection_name='posts',
            vectors_config={
                'post': VectorParams(size=vector_size, distance=Distance.COSINE),
                'thread': VectorParams(size=vector_size, distance=Distance.COSINE)
            }
        )

    if not await qdrant.collection_exists('users'):
        qdrant.create_collection(
            collection_name='users',
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

    if not await qdrant.collection_exists('bots'):
        qdrant.create_collection(
            collection_name='bots',
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_qdrant_collections(qdrant_client, settings.embeddings_vector_size)

    yield
    
    await qdrant_client.close()

app = FastAPI(lifespan=lifespan, title='Xter FastAPI Service')

app.include_router(router)