from typing import List

from app.domain.batches.base_batch import BaseBatch
from app.domain.jobs.retrain_user_embedding_job import RetrainUserEmbeddingJob
from app.repositories.redis_repo import RedisRepo
from app.core.exceptions import UserBusy, NoJobsToProcess


class RetrainUserEmbeddingBatch:
    _redis: RedisRepo = RedisRepo(namespace='retrain')

    def __init__(self):
        self._jobs: List[RetrainUserEmbeddingJob] = []

    def __iter__(self):
        return iter(self._jobs)

    def __len__(self) -> int:
        return len(self._jobs)
    
    def __bool__(self):
        return bool(self._jobs)
    
    def add_jobs(self, jobs: List[RetrainUserEmbeddingJob]):
        self._jobs.extend(jobs)

    def remove_jobs(self):
        self._redis.remove_jobs(job.job_id for job in self._jobs)
    
    @property
    def jobs(self) -> List[RetrainUserEmbeddingJob]:
        return self._jobs
    
    @classmethod
    def build(cls, initial_user_id: int | None = None, limit: int = 50):
        batch = cls()

        with batch._redis.lock() as (acquire, acquire_next_user):
            if initial_user_id is not None:
                acquired = acquire(initial_user_id)

                if not acquired:
                    return
            
                new_jobs = RetrainUserEmbeddingJob.get_jobs(user_id=initial_user_id, limit=limit)
                batch.add_jobs(new_jobs)
            
            while len(batch) < limit:
                user_id = acquire_next_user()

                if not user_id:
                    break

                new_jobs = RetrainUserEmbeddingJob.get_jobs(user_id=user_id, limit=limit - len(batch))
                batch.add_jobs(new_jobs)

            batch.remove_jobs()

        return batch