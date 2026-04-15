import numpy as np
from typing import ClassVar

from app.core.exceptions import EmbeddingBusy, UserBusy, NoJobsToProcess
from app.core.fastembed import embedder
from app.domain.jobs.create_post_embeddings_job import CreatePostEmbeddingsJob
from app.domain.jobs.retrain_user_embedding_job import RetrainUserEmbeddingJob
from app.domain.batches.create_post_embeddings_batch import CreatePostEmbeddingsBatch
from app.domain.batches.retrain_user_embedding_batch import RetrainUserEmbeddingBatch
from app.repositories.qdrant_repo import QdrantRepo
from app.repositories.redis_repo import RedisRepo
from app.utils.embedding_calculator import calculate_retrained_embedding


class UserEmbeddingService:
    async def handle_request(self, job: RetrainUserEmbeddingJob):
        job.enqueue()

        worker = UserEmbeddingWorker()
        await worker.launch(job.user_id)

class UserEmbeddingWorker:
    def __init__(self):
        self.qdrant = QdrantRepo()
        self.redis = RedisRepo(namespace='retrain')

    async def launch(self, user_id: int):
        await self.run(user_id=user_id)

    async def run(self, user_id: int | None = None, limit: int = 50):
        batch = RetrainUserEmbeddingBatch.build(initial_user_id=user_id, limit=limit)

        if not batch:
            return
        
        await self.retrain(batch)
        await self.run(limit=limit)


    async def retrain(self, batch: RetrainUserEmbeddingBatch):
        user_ids, post_ids = map(set, zip(*((job.user_id, job.post_id) for job in batch)))

        user_embeddings = await self.qdrant.get_user_embeddings(user_ids)
        post_embeddings = await self.qdrant.get_post_embeddings(post_ids)

        jobs_by_user = {}

        for job in batch:
            jobs_by_user.setdefault(job.user_id, []).append(job)

        retrained_embeddings = {}

        for user_id, jobs in jobs_by_user.items():
            u0 = user_embeddings.get(user_id, np.zeros(384, dtype=np.float32))

            posts = np.stack([post_embeddings[job.post_id] for job in jobs], axis=0).astype(np.float32)
            alphas = np.array([job.alpha for job in jobs], dtype=np.float32)

            u_new = calculate_retrained_embedding(u0, posts, alphas)

            retrained_embeddings[user_id] = u_new

        await self.qdrant.upsert_user_embeddings(retrained_embeddings)


class PostEmbeddingsService:
    async def handle_request(self, job: CreatePostEmbeddingsJob):
        job.enqueue()

        worker = PostEmbeddingsWorker()
        await worker.launch()

class PostEmbeddingsWorker:
    def __init__(self):
        self.qdrant = QdrantRepo()
        self.redis = RedisRepo(namespace='embed')

    async def launch(self):
        await self.run()

    async def run(self, limit: int = 50):
        batch = CreatePostEmbeddingsBatch.build(limit=limit)

        if not batch:
            return
        
        await self.embed(batch)
        await self.run()

    async def embed(self, batch: CreatePostEmbeddingsBatch):
        meta, texts = batch.get_texts()
        embeddings = embedder.embed(texts)
        
        data = {}

        for (content_type, post_id), embedding in zip(meta, embeddings):
            entry = data.setdefault(post_id, {})
            entry[content_type] = embedding.tolist()
            entry['timestamp'] = int(batch._jobs[0].timestamp)

        await self.qdrant.upsert_post_embeddings(data)