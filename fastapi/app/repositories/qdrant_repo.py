from datetime import datetime, timedelta, timezone
from heapq import nlargest
from itertools import chain
from typing import ClassVar
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, Range, Query

from app.core.qdrant import qdrant_client
from app.core.config import settings

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


    def post_embeddings_exist(self, post_id: int) -> bool:
        points = self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=[post_id]
        )

        return len(points) > 0


    async def upsert_post_embeddings(self, data: dict):
        points = [
            PointStruct(
                id=post_id,
                vector=payload.get('embeddings'),
                payload={
                    'timestamp': payload.get('timestamp')
                }
            ) for post_id, payload in data.items()
        ]

        self.qdrant.upsert(
            collection_name=self.post_collection,
            points=points
        )

    async def upsert_user_embeddings(self, data: dict):
        points = [
            PointStruct(
                id=user_id,
                vector=payload.get('embedding')
            ) for user_id, payload in data.items()
        ]

        self.qdrant.upsert(
            collection_name=self.user_collection,
            points=points
        )

    async def get_post_embeddings(self, post_ids: list[int]) -> dict[int, dict[str, list[float]]]:
        points = self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=post_ids,
            with_vectors=True
        )

        return {
            point.id: point.vector for point in points
        }
    
    async def get_user_embeddings(self, user_ids: list[int]) -> dict[int, list[float]]:
        points = self.qdrant.retrieve(
            collection_name=self.user_collection,
            ids=user_ids,
            with_vectors=True
        )

        return {
            point.id: point.vector for point in points
        }
    

    async def get_recommendations(self, user_id: int, limit: int, delta: timedelta) -> dict[int, float]:
        embeddings = await self.get_user_embeddings([user_id])
        user_vector = embeddings.get(user_id, [0] * settings.embeddings_vector_size)

        now = datetime.now(timezone.utc)
        threshold = (now - delta).timestamp()

        post_hits = self.qdrant.query_points(
            collection_name=self.post_collection,
            query=user_vector,
            limit=limit,
            using='post',
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key='timestamp',
                        range=Range(
                            gte=threshold
                        )
                    )
                ]
            )
        )

        thread_hits = self.qdrant.query_points(
            collection_name=self.post_collection,
            query=user_vector,
            limit=limit,
            using='thread',
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key='timestamp',
                        range=Range(
                            gte=threshold
                        )
                    )
                ]
            )
        )

        deduped = {}

        for point in chain(post_hits.points, thread_hits.points):
            if point.score > deduped.get(point.id, 0):
                deduped[point.id] = point.score

        result = dict(nlargest(limit, deduped.items(), key=lambda x: x[1]))

        return result