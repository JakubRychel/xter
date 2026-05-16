import asyncio
from datetime import datetime, timedelta, timezone
from heapq import nlargest
from itertools import chain
from qdrant_client.models import PointStruct, Filter, FieldCondition, HasIdCondition, Range

from app.core.config import settings


class QdrantRepo:
    def __init__(self, qdrant_client):
        self.qdrant = qdrant_client

        self.post_collection = 'posts'
        self.user_collection = 'users'
        self.bot_collection = 'bots'

    async def post_embeddings_exist(self, post_id: int) -> bool:
        points = await self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=[post_id]
        )

        return len(points) > 0


    async def upsert_post_embeddings(self, data: dict) -> bool:
        points = [
            PointStruct(
                id=post_id,
                vector=payload.get('embeddings'),
                payload={
                    'timestamp': payload.get('timestamp')
                }
            ) for post_id, payload in data.items()
        ]

        result = await self.qdrant.upsert(
            collection_name=self.post_collection,
            points=points
        )

        return result.status in ('completed', 'acknowledged')

    async def upsert_user_embeddings(self, data: dict):
        points = [
            PointStruct(
                id=user_id,
                vector=payload.get('embedding')
            ) for user_id, payload in data.items()
        ]

        result = await self.qdrant.upsert(
            collection_name=self.user_collection,
            points=points
        )

        return result.status in ('completed', 'acknowledged')

    async def upsert_bot_embedding(self, data: dict):
        points = [
            PointStruct(
                id=data.get('bot_id'),
                vector=data.get('embedding')
            )
        ]

        result = await self.qdrant.upsert(
            collection_name=self.bot_collection,
            points=points
        )

        return result.status in ('completed', 'acknowledged')

    async def get_post_embeddings(self, post_ids: list[int]) -> dict[int, dict[str, list[float]]]:
        points = await self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=post_ids,
            with_vectors=True
        )

        return {
            point.id: point.vector for point in points
        }
    
    async def get_user_embeddings(self, user_ids: list[int]) -> dict[int, list[float]]:
        points = await self.qdrant.retrieve(
            collection_name=self.user_collection,
            ids=user_ids,
            with_vectors=True
        )

        return {
            point.id: point.vector for point in points
        }
    

    async def get_recommendations(
        self,
        user_id: int,
        chunks: list[tuple[int, tuple[timedelta | None, timedelta | None]]]
    ) -> dict[int, float]:
        
        embeddings = await self.get_user_embeddings([user_id])
        user_vector = embeddings.get(user_id, [0] * settings.embeddings_vector_size)

        now = datetime.now(timezone.utc)

        tasks = []

        for limit, (start, end) in chunks:
            range_kwargs = {}

            if start is not None:
                range_kwargs['lt'] = (now - start).timestamp()

            if end is not None:
                range_kwargs['gte'] = (now - end).timestamp()

            query_filter = Filter(
                must=[
                    FieldCondition(
                        key='timestamp',
                        range=Range(**range_kwargs)
                    )
                ]
            ) if range_kwargs else None

            tasks.append(
                self.qdrant.query_points(
                    collection_name=self.post_collection,
                    query=user_vector,
                    limit=limit,
                    using='post',
                    query_filter=query_filter
                )
            )

            tasks.append(
                self.qdrant.query_points(
                    collection_name=self.post_collection,
                    query=user_vector,
                    limit=limit,
                    using='thread',
                    query_filter=query_filter
                )
            )

        results = await asyncio.gather(*tasks)

        deduped = {}

        for result in results:
            for point in result.points:
                if point.score > deduped.get(point.id, float('-inf')):
                    deduped[point.id] = point.score

        total_limit = sum(limit for limit, _ in chunks)

        return dict(nlargest(total_limit, deduped.items(), key=lambda x: x[1]))
    
    async def get_post_scores(self, user_id: int, post_ids: list[int]) -> dict[int, float]:
        embeddings = await self.get_user_embeddings([user_id])
        user_vector = embeddings.get(user_id, [0] * settings.embeddings_vector_size)

        post_points = await self.qdrant.query_points(
            collection_name=self.post_collection,
            query=user_vector,
            limit=len(post_ids),
            using='post',
            query_filter=Filter(
                must=[
                    HasIdCondition(has_id=post_ids)
                ]
            )
        )

        thread_points = await self.qdrant.query_points(
            collection_name=self.post_collection,
            query=user_vector,
            limit=len(post_ids),
            using='thread',
            query_filter=Filter(
                must=[
                    HasIdCondition(has_id=post_ids)
                ]
            )
        )

        deduped = {}

        for point in chain(post_points.points, thread_points.points):
            if point.score > deduped.get(point.id, float('-inf')):
                deduped[point.id] = point.score

        return deduped
    
    async def get_thread_score_for_bot(self, bot_id: int, post_id: int) -> float:
        bot_points = await self.qdrant.retrieve(
            collection_name=self.bot_collection,
            ids=[bot_id],
            with_vectors=True
        )

        if not bot_points:
            raise ValueError('Bot not found.')

        bot_vector = bot_points[0].vector

        post_points = await self.qdrant.query_points(
            collection_name=self.post_collection,
            query=bot_vector,
            limit=1,
            using='thread',
            query_filter=Filter(
                must=[
                    HasIdCondition(has_id=[post_id])
                ]
            )
        )

        if not post_points.points:
            raise ValueError('Post not found.')

        score = post_points.points[0].score

        return score