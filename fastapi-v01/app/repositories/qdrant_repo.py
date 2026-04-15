import asyncio
from app.core.qdrant import qdrant_client
from fastapi.concurrency import run_in_threadpool
from qdrant_client.http.models import PointStruct

class QdrantRepo:
    def __init__(self):
        self.qdrant = qdrant_client
        self.post_collection = 'posts'
        self.user_collection = 'users'

        if not self.qdrant.has_collection(self.post_collection):
            self.qdrant.create_collection(
                collection_name=self.post_collection,
                vectors={
                    'post': VectorParams(size=384, distance=Distance.COSINE),
                    'thread': VectorParams(size=384, distance=Distance.COSINE)
                }
            )

        if not self.qdrant.has_collection(self.user_collection):
            self.qdrant.create_collection(
                collection_name=self.user_collection,
                vector=VectorParams(size=384, distance=Distance.COSINE)
            )

    def post_embedding_exists(self, post_id: int) -> bool:
        points = self.qdrant.retrieve(
            collection_name=self.post_collection,
            ids=[post_id]
        )

        return len(points) > 0
    
    async def get_post_embeddings(self, post_ids: list):
        points = await run_in_threadpool(
            self.qdrant.retrieve,
            collection_name=self.post_collection,
            ids=[post_ids],
            with_vectors=True,
            with_payload=True
        )

        return {point.id: point.vectors for point in points}
    
    async def update_post_embeddings(self, items: list):
        points = [PointStruct(
            id=item['id'],
            vectors=item['vectors'],
            payload={'post_id': item['id']}
        ) for item in items]

        await run_in_threadpool(
            self.qdrant.upsert,
            collection_name=self.post_collection,
            points=points
        )

    
    async def get_user_embeddings(self, user_ids: list):
        points = await run_in_threadpool(
            self.qdrant.retrieve,
            collection_name=self.user_collection,
            ids=[user_ids],
            with_vectors=True,
            with_payload=True
        )

        return {point.id: point.vector for point in points}
    
    async def update_user_embeddings(self, items: list):
        points = [PointStruct(
            id=item['id'],
            vector=item['vector'],
            payload={'user_id': item['id']}
        ) for item in items]

        await run_in_threadpool(
            self.qdrant.upsert,
            collection_name=self.user_collection,
            points=points
        )

    async def get_recommendations(self, user_id: int, limit: int):
        user_embeddings = await self.get_user_embeddings([user_id])
        user_embedding = user_embeddings[user_id]

        post_points, thread_points = await asyncio.gather(
            run_in_threadpool(
                self.qdrant.search,
                collection_name=self.post_collection,
                query_vector=user_embedding,
                vector_name='post',
                limit=limit
            ),
            run_in_threadpool(
                self.qdrant.search,
                collection_name=self.post_collection,
                query_vector=user_embedding,
                vector_name='thread',
                limit=limit
            )
        )

        posts, threads = map(lambda points: {point.id: point.score for point in points}, (post_points, thread_points))

        return posts, threads