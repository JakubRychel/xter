from datetime import datetime, timedelta
from heapq import nlargest
from itertools import chain

from qdrant_client.http.models import VectorParams, Distance, PointStruct
from app.core.qdrant import qdrant_client
from app.core.config import settings

from typing import ClassVar

class QdrantRepo:
    _instance: ClassVar['QdrantRepo' | None] = None

    def __new__(cls):
        if not cls._instance:
            instance = super().__new__(cls)
            instance._init()
            cls._instance = instance

        return cls._instance

    def _init(self):
        self.qdrant = qdrant_client
        self.post_collection = 'posts'
        self.user_collection = 'users'

        VECTOR_SIZE = settings.embeddings_vector_size

        if not self.qdrant.collection_exists(self.post_collection):
            self.qdrant.create_collection(
                collection_name=self.post_collection,
                vectors_config={
                    'post': VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                    'thread': VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
                }
            )

        if not self.qdrant.collection_exists(self.user_collection):
            self.qdrant.create_collection(
                collection_name=self.user_collection,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )

    

    def post_embeddings_exist(self, post_id: int) -> list:
        points = self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=[post_id]
        )

        return len(points) > 0

    async def upsert_post_embeddings(self, data: list[dict]):
        points = [
            PointStruct(
                id=post_id,
                vector={
                    'post': entry.get('post'),
                    'thread': entry.get('thread')
                },
                payload={
                    'timestamp': entry.get('timestamp')
                }
            ) for post_id, entry in data.items()
        ]

        self.qdrant.upsert(
            collection_name=self.post_collection,
            points=points
        )

    async def upsert_user_embeddings(self, data: list[dict]):
        points = [
            PointStruct(
                id=entry.get('user_id'),
                vector=entry.get('embedding')
            ) for entry in data
        ]

        self.qdrant.upsert(
            collection_name=self.user_collection,
            points=points
        )

    async def get_post_embeddings(self, post_ids: list[int]) -> dict[int, dict[str, list[float]]]:
        points = self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=post_ids
        )

        return {
            point.id: point.vector for point in points
        }
    
    async def get_user_embeddings(self, user_ids: list[int]) -> dict[int, list[float]]:
        points = self.qdrant.retrieve(
            collection_name=self.user_collection,
            ids=user_ids
        )

        return {
            point.id: point.vector for point in points
        }

    async def get_recommended_posts(self, user_id: int, limit: int, delta: timedelta) -> dict[int, float]:
        user_vector = self.get_user_embeddings([user_id])[user_id]

        now = datetime.now()
        threshold = now - delta

        post_hits = self.qdrant.search(
            collection_name=self.post_collection,
            query_vector=user_vector,
            query_filter={
                'must': [
                    {
                        'key': 'timestamp',
                        'range': {
                            'gte': threshold.timestamp()
                        }
                    }
                ]
            },
            using='post',
            limit=limit
        )

        thread_hits = self.qdrant.search(
            collection_name=self.post_collection,
            query_vector=user_vector,
            query_filter={
                'must': [
                    {
                        'key': 'timestamp',
                        'range': {
                            'gte': threshold.timestamp()
                        }
                    }
                ]
            },
            using='thread',
            limit=limit
        )

        deduped = {}

        for hit in chain(post_hits, thread_hits):
            if hit.score > deduped.get(hit.id, 0):
                deduped[hit.id] = hit.score

        result = dict(nlargest(limit, deduped, key=deduped.get))

        return result

    



    async def fetch_user_embedding(self, user_id: int) -> list[float] | None:
        points = self.qdrant.retrieve(
            collection_name=self.user_collection,
            ids=[user_id],
            with_vectors=True
        )
        
        return points[0].vector if points and points[0].vector is not None else None
    
    async def fetch_post_embeddings(self, post_id: int) -> tuple[list[float] | None, list[float] | None]:
        points = self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=[post_id],
            with_vectors=True
        )
        
        if not points:
            return None, None

        vector = points[0].vector
        if vector is None:
            return None, None
        
        return vector.get('post'), vector.get('thread')
    
    async def fetch_all_user_embeddings(self) -> dict[int, list[float]]:
        # Pobierz wszystkie punkty z kolekcji użytkowników
        points = self.qdrant.scroll(
            collection_name=self.user_collection,
            limit=10000,  # Dostosuj limit w zależności od potrzeb
            with_vectors=True
        )[0]
        
        return {point.id: point.vector for point in points}
    
    async def fetch_all_post_embeddings(self) -> dict[int, dict[str, list[float]]]:
        # Pobierz wszystkie punkty z kolekcji postów
        points = self.qdrant.scroll(
            collection_name=self.post_collection,
            limit=10000,  # Dostosuj limit w zależności od potrzeb
            with_vectors=True
        )[0]
        
        return {point.id: point.vector for point in points}