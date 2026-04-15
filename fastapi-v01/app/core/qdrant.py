from qdrant_client import QdrantClient

qdrant_client = QdrantClient(url='http://qdrant:6333', prefer_grpc=False)