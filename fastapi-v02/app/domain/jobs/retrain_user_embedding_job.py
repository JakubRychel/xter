from contextlib import contextmanager


from .base_job import BaseJob
from app.core.exceptions import NoJobsToProcess, UserBusy
from app.repositories.redis_repo import RedisRepo
from app.repositories.qdrant_repo import QdrantRepo
from typing import ClassVar, List


class RetrainUserEmbeddingJob(BaseJob):
    _redis: ClassVar['RedisRepo'] = RedisRepo(namespace='retrain')
    _qdrant: ClassVar['QdrantRepo'] = QdrantRepo()

    job_id: int | None = None

    user_id: int
    post_id: int
    alpha: float

    @classmethod
    def get_jobs(cls, user_id: int, limit: int):
        raw_jobs = cls._redis.get_jobs(user_id=user_id, limit=limit)

        if not raw_jobs:
            return []

        jobs = [
            cls(
                job_id = raw_job['job_id'],
                **raw_job['payload']
            ) for raw_job in raw_jobs
        ]

        return jobs

    def enqueue(self):
        if not (self._qdrant.post_embeddings_exist(self.post_id) or self._redis.is_post_queued(self.post_id)):
            raise ValueError('Post embedding does not exist.')
        
        payload = {
            'user_id': self.user_id,
            'post_id': self.post_id,
            'alpha': self.alpha
        }
    
        self._redis.enqueue_job(payload)

    def get(self):
        raise NotImplementedError()

    def remove(self):
        raise NotImplementedError()