import numpy as np
from typing import Literal
from fastapi.concurrency import run_in_threadpool
from qdrant_client.http.models import PointStruct
from app.core.qdrant import qdrant_client
from app.core.fastembed import FastEmbedService
from app.schemas.embeddings_schema import GeneratePostEmbeddingRequest
from app.repositories.redis_repo import RedisRepo
from app.repositories.qdrant_repo import QdrantRepo
from fastapi.app.jobs.retrain_user_embedding_job import RetrainUserEmbeddingJob


class UserBusy(Exception):
    pass
class NoJobsToProcess(Exception):
    pass

class PostEmbeddingService:
    def __init__(self):
        self.qdrant = QdrantRepo()
        self.redis = RedisRepo()
        self.embed_service = FastEmbedService()
        self.post_collection = 'posts'

    async def handle_generate_post_embeddings_request(
        self,
        post_id: int,
        post_content: str,
        thread_content: str | None = None
    ):
        with self.redis.post_embeddings_generating_lock() as locked:
            if not locked:
                self.redis.enqueue_generate_post_embeddings_job(post_id, post_content, thread_content)
                return
            
            jobs = [self.redis.create_generate_post_embeddings_job(post_id, post_content, thread_content)]
            batch = self.redis.build_generate_post_embeddings_batch(jobs=jobs)

            await self.generate_embeddings(batch)

    async def generate_embeddings(self, batch: list):
        items = []

        for job in batch:
            items.append({
                'post_id': job['post_id'],
                'embedding_type': 'post',
                'text': job['post_content']
            })

            if job['thread_content'] is not None:
                items.append({
                    'post_id': job['post_id'],
                    'embedding_type': 'thread',
                    'text': job['thread_content']
                })

        texts = [item['text'] for item in items]
        embeddings = list(self.embed_service.embed(texts))

        payload = {}

        for item, embedding in zip(items, embeddings):
            id = item['post_id']
            type = item['embedding_type']

            payload[id][type] = embedding
        
        await self.qdrant.update_post_embeddings(payload)


class RetrainUserEmbeddingJobsBatcher:
    def __init__(self):
        self.redis = RedisRepo()
        self.locked_user_ids: list[int] = []

    def __enter__(self):
        return self
    
    def __exit__(self):
        self.redis.unlock_users(self.locked_user_ids)

    def acquire_lock(self, user_id: int) -> bool:
        return self.redis.lock_user(user_id)

class UserEmbeddingService:
    def __init__(self):
        self.qdrant = QdrantRepo()
        self.redis = RedisRepo()
        self.post_collection = 'posts'
        self.user_collection = 'users'

    async def handle_retrain_request(self, user_id: int, post_id: int, alpha: float):
        if not (self.qdrant.post_embedding_exists(post_id) or self.redis.is_post_queued(post_id)):
            return

        job = RetrainUserEmbeddingJob.create(user_id=user_id, post_id=post_id, alpha=alpha)
        job.enqueue()

        try:
            await self.process_retraining(user_id=user_id)

            while True:
                await self.process_retraining()

        except NoJobsToProcess:
            pass

    async def process_retraining(self, user_id: int | None = None, limit: int = 50):
        pass
        def get_next_user_id():
            if user_id is not None:
                yield user_id

            while True:
                next_user_id = self.redis.get_next_user_id()

                if next_user_id is None:
                    break

                yield next_user_id

        with UserLock() as lock:
            for user_id in get_next_user_id():





        job_ids: list[int] = []
        locked_user_ids: list[int] = []

        def get_next_user_id():
            if user_id is not None:
                yield user_id

            while True:
                next_user_id = self.redis.get_next_user_id()

                if next_user_id is None:
                    break

                yield next_user_id

        try:
            for next_user_id in get_next_user_id():
                remaining = limit - len(job_ids)

                if remaining <= 0:
                    break

                locked = self.redis.lock_user(next_user_id)

                if not locked:
                    if user_id is not None and next_user_id == user_id:
                        raise UserBusy()
                    
                    continue

                locked_user_ids.append(next_user_id)

                new_job_ids = self.redis.get_job_ids(next_user_id, remaining)

                if new_job_ids:
                    job_ids.extend(new_job_ids)

            if not job_ids:
                raise NoJobsToProcess()

            jobs = self.redis.pop_jobs(job_ids)

            await self.retrain_embeddings(jobs)
                    
        finally:
            self.redis.unlock_users(locked_user_ids)

    async def retrain_embeddings(self, batch: list):
        user_ids, post_ids = map(set, zip(*((job['user_id'], job['post_id']) for job in batch)))

        user_embeddings = await self.qdrant.get_user_embeddings(user_ids)
        post_embeddings = await self.qdrant.get_post_embeddings(post_ids)

        jobs_by_user = {}

        for job in batch:
            jobs_by_user.setdefault(job['user_id'], []).append(job)

        retrained_embeddings = []

        for user_id, jobs in jobs_by_user.items():
            u0 = user_embeddings.get(user_id, np.zeros(384, dtype=np.float32))

            posts = np.stack([post_embeddings[job['post_id']] for job in jobs], axis=0).astype(np.float32)
            alphas = np.array([job['alpha'] for job in jobs], dtype=np.float32)

            N = len(alphas)

            suffix = np.ones(N, dtype=np.float32)
            for i in range(N-2, -1, -1):
                suffix[i] = suffix[i+1] * (1.0 - alphas[i+1])

            w_posts = alphas * suffix
            w0 = np.prod(1.0 - alphas)

            u_new = w0 * u0 + (w_posts[:, None] * posts).sum(axis=0)

            retrained_embeddings.append({
                'id': user_id,
                'vector': u_new
            })

        await self.qdrant.update_user_embeddings(retrained_embeddings)