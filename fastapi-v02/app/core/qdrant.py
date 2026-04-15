from qdrant_client import QdrantClient
from .config import settings

qdrant_client = QdrantClient(
    url=f'http://{settings.qdrant_host}:{settings.qdrant_port}',
    api_key=settings.qdrant_api_key,
    prefer_grpc=False
)