from app.repositories.qdrant_repo import QdrantRepo
from app.repositories.redis_repo import RedisRepo
from app.core.exceptions import NoJobsToProcess
from .base_job import BaseJob

from typing import ClassVar

class CreatePostEmbeddingsJob(BaseJob):
    _redis: ClassVar['RedisRepo'] = RedisRepo(namespace='embed')
    _qdrant: ClassVar['QdrantRepo'] = QdrantRepo()

    job_id: int | None = None

    post_id: int
    post_content: str
    thread_content: str
    timestamp: int

    @classmethod
    def get_jobs(cls, limit: int = 50):
        raw_jobs = cls._redis.get_jobs(limit=limit)

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
        payload = {
            'post_id': self.post_id,
            'post_content': self.post_content,
            'thread_content': self.thread_content,
            'timestamp': self.timestamp
        }

        self._redis.enqueue_job(payload)