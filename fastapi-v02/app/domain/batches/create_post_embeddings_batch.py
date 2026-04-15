from typing import List

from app.repositories.redis_repo import RedisRepo
from app.core.exceptions import EmbeddingBusy
from app.domain.jobs.create_post_embeddings_job import CreatePostEmbeddingsJob


class CreatePostEmbeddingsBatch:
    _redis: RedisRepo = RedisRepo(namespace='embed')

    def __init__(self):
        self._jobs: List[CreatePostEmbeddingsJob] = []

    def __iter__(self):
        return iter(self._jobs)

    def __len__(self) -> int:
        return len(self._jobs)
    
    def __bool__(self):
        return bool(self._jobs)

    def add_jobs(self, jobs: List[CreatePostEmbeddingsJob]):
        self._jobs.extend(jobs)

    def remove_jobs(self):
        self._redis.remove_jobs([job.job_id for job in self._jobs])

    @classmethod
    def build(cls, limit: int = 50):
        batch = cls()

        with batch._redis.lock() as acquire:
            acquired = acquire()

            if not acquired:
                return

            new_jobs = CreatePostEmbeddingsJob.get_jobs(limit=limit)
            batch.add_jobs(new_jobs)

            batch.remove_jobs()

        return batch
    
    def get_texts(self) -> tuple[List[dict], List[str]]:
        meta = []
        texts = []

        for job in self._jobs:
            meta.append(('post', job.post_id))
            texts.append(job.post_content)

            if job.thread_content:
                meta.append(('thread', job.post_id))
                texts.append(job.thread_content)

        return meta, texts