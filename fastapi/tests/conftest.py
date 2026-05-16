import pytest
from fastapi.testclient import TestClient
from main import app

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance

from app.repositories.qdrant_repo import QdrantRepo

client = TestClient(app)

VECTOR_SIZE = 384

@pytest.fixture
async def qdrant_repo():
    client = AsyncQdrantClient(':memory:')

    await client.create_collection(
        collection_name='posts',
        vectors_config={
            'post': VectorParams(size = VECTOR_SIZE, distance = Distance.COSINE),
            'thread': VectorParams(size = VECTOR_SIZE, distance = Distance.COSINE)
        }
    )

    await client.create_collection(
        collection_name='users',
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )