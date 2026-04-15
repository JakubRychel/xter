from itertools import chain, groupby
import numpy as np

from app.core.config import settings
from app.core.fastembed import embedder
from app.repositories.redis_repo import RedisRepo
from app.repositories.qdrant_repo import QdrantRepo
from app.schemas.embeddings_schema import CreatePostEmbeddingsJob, RetrainUserEmbeddingJob
from app.utils.embedding_calculator import calculate_retrained_embedding


class PostEmbeddingsService:
    def __init__(self):
        self.redis = RedisRepo(namespace='embed')
        self.qdrant = QdrantRepo()

    async def handle_request(self, job: CreatePostEmbeddingsJob):
        self.redis.enqueue_job(job)

        await self.run()

    async def run(self, limit: int = 50):
        batch = self.build_batch(limit=limit)

        if not batch:
            return
        
        await self.embed(batch)
        await self.run(limit=limit)

    async def embed(self, batch: list[CreatePostEmbeddingsJob]):
        data = {
            job.post_id: {
                'timestamp': job.timestamp,
                'embeddings': {}
            } for job in batch
        }

        items = chain(
            ((job.post_content, (job.post_id, 'post')) for job in batch),
            ((job.thread_content, (job.post_id, 'thread')) for job in batch if job.thread_content)
        )

        texts, meta = zip(*items)

        embeddings = list(embedder.embed(texts))

        for embedding, (post_id, text_type) in zip(embeddings, meta):
            data[post_id]['embeddings'][text_type] = list(embedding)

        await self.qdrant.upsert_post_embeddings(data)
        

    def build_batch(self, limit: int = 50) -> list[CreatePostEmbeddingsJob]:
        jobs = []

        with self.redis.lock() as acquire:
            acquired = acquire()

            if not acquired:
                return []
            
            new_jobs = self.redis.get_jobs(limit=limit)
            jobs.extend(new_jobs)

            self.redis.remove_jobs(jobs)

        return jobs

class UserEmbeddingsService:
    def __init__(self):
        self.redis = RedisRepo(namespace='retrain')
        self.qdrant = QdrantRepo()

    async def handle_request(self, job: RetrainUserEmbeddingJob):
        self.redis.enqueue_job(job)

        await self.run(user_id=job.user_id)

    async def run(self, user_id: int | None = None, limit: int = 50):
        batch = self.build_batch(initial_user_id=user_id, limit=limit)

        if not batch:
            return
        
        await self.retrain(batch)
        await self.run(limit=limit)

    async def retrain(self, batch: list[RetrainUserEmbeddingJob]):
        DIM = settings.embeddings_vector_size

        jobs_by_user = {
            user_id: list(jobs) for user_id, jobs in groupby(batch, lambda job: job.user_id)
        }

        user_ids = list(jobs_by_user.keys())
        post_ids = list(set(job.post_id for job in batch))

        user_embeddings = await self.qdrant.get_user_embeddings(user_ids)
        post_embeddings = await self.qdrant.get_post_embeddings(post_ids)

        retrained_embeddings = {}

        for user_id, jobs in jobs_by_user.items():
            u0 = user_embeddings.get(user_id, np.zeros(DIM, dtype=np.float32))

            posts = np.stack([post_embeddings[job.post_id]['post'] for job in jobs], axis=0).astype(np.float32)
            alphas = np.array([job.alpha for job in jobs], dtype=np.float32)

            u_new = calculate_retrained_embedding(u0, posts, alphas)

            retrained_embeddings[user_id] = {'embedding': u_new.tolist()}

        await self.qdrant.upsert_user_embeddings(retrained_embeddings)


    def build_batch(self, initial_user_id: int | None = None, limit: int = 50) -> list[RetrainUserEmbeddingJob]:
        jobs = []

        with self.redis.lock() as (acquire, acquire_next_user):
            if initial_user_id is not None:
                acquired = acquire(initial_user_id)

                if not acquired:
                    return []
                
                new_jobs = self.redis.get_jobs(user_id=initial_user_id, limit=limit)
                jobs.extend(new_jobs)
            
            while len(jobs) < limit:
                user_id = acquire_next_user()

                if not user_id:
                    break
                
                new_jobs = self.redis.get_jobs(user_id=user_id, limit=limit - len(jobs))
                jobs.extend(new_jobs)

            self.redis.remove_jobs(jobs)

        return sorted(jobs, key=lambda job: job.user_id)