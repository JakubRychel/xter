from itertools import groupby
import json
from typing import ClassVar
from contextlib import contextmanager

from app.core.redis import redis_client
from app.schemas.embeddings_schema import CreatePostEmbeddingsJob, RetrainUserEmbeddingJob

KEYS = {
    'embed': {
        'COUNTER': 'embed:counter',
        'JOBS': 'embed:jobs',
        'QUEUE': 'embed:queue',
        'LOCK': 'embed:lock'
    },
    'retrain': {
        'COUNTER': 'retrain:counter',
        'JOBS': 'retrain:jobs',
        'GLOBAL': 'retrain:global',
        'USER': 'retrain:user:{}',
        'LOCK': 'retrain:lock:{}'
    }
}

class RedisRepo:
    _instances: ClassVar[dict[str, 'RedisRepo']] = {}

    def __new__(cls, namespace: str):
        if namespace not in cls._instances:
            instance = super().__new__(cls)
            instance._init(namespace)
            cls._instances[namespace] = instance

        return cls._instances[namespace]
    
    def _init(self, namespace: str):
        self.redis = redis_client
        self.namespace = namespace

        for name, value in KEYS[namespace].items():
            setattr(self, name, value)

        if namespace == 'embed':
            self.lock = self._embed_lock
            self.enqueue_job = self._embed_enqueue_job
            self.get_jobs = self._embed_get_jobs
            self.remove_jobs = self._embed_remove_jobs

        if namespace == 'retrain':
            self.lock = self._retrain_lock
            self.enqueue_job = self._retrain_enqueue_job
            self.get_jobs = self._retrain_get_jobs
            self.remove_jobs = self._retrain_remove_jobs
            self.get_user_ids = self._retrain_get_user_ids
            self.update_global_queue = self._retrain_update_global_queue


    def is_post_queued(self, post_id: int) -> bool:
        return self.redis.zscore(KEYS['embed']['QUEUE'], post_id) is not None
    

    @contextmanager
    def _embed_lock(self, expire: int = 60):
        def acquire() -> bool:
            acquired = self.redis.set(self.LOCK, 1, nx=True, ex=expire)
            return acquired
        
        try:
            yield acquire

        finally:
            self.redis.delete(self.LOCK)

    def _embed_enqueue_job(self, job: CreatePostEmbeddingsJob):
        job_id = self.redis.incr(self.COUNTER)
        post_id = job.post_id

        old_job_id = self.redis.zscore(self.QUEUE, post_id)

        data = job.model_dump()
        data['job_id'] = job_id

        print(data)

        self.redis.zadd(self.QUEUE, {post_id: job_id})
        self.redis.hset(self.JOBS, job_id, json.dumps(data))

        if old_job_id is not None:
            self.redis.hdel(self.JOBS, int(old_job_id))

    def _embed_get_jobs(self, limit: int = 50) -> list[CreatePostEmbeddingsJob]:
        data = self.redis.zrange(self.QUEUE, 0, limit - 1, withscores=True)

        if not data:
            return []
        
        members, scores = zip(*data)

        job_ids = [int(score) for score in scores]
        
        raw_jobs = self.redis.hmget(self.JOBS, job_ids)
        jobs = [CreatePostEmbeddingsJob(**json.loads(raw_job)) for raw_job in raw_jobs if raw_job is not None]

        return jobs
    
    def _embed_remove_jobs(self, jobs: list[CreatePostEmbeddingsJob]):
        if not jobs:
            return

        job_ids = [job.job_id for job in jobs]

        self.redis.zremrangebyscore(self.QUEUE, min(job_ids), max(job_ids))
        self.redis.hdel(self.JOBS, *job_ids)


    @contextmanager
    def _retrain_lock(self):
        locked_user_ids = set()

        def acquire(user_id: int, expire: int = 60) -> bool:
            acquired = self.redis.set(self.LOCK.format(user_id), 1, nx=True, ex=expire)

            if acquired:
                print(f'Acquired lock for user {user_id}')
                locked_user_ids.add(user_id)

            return acquired
        
        def acquire_next_user() -> int | None:
            user_ids = self.get_user_ids()

            if not user_ids:
                return None
            
            for user_id in user_ids:
                acquired = acquire(user_id)

                if acquired:
                    return user_id
                
        try:
            yield acquire, acquire_next_user

        finally:
            if locked_user_ids:
                print (f'Releasing locks for users: {locked_user_ids}')
                self.redis.delete(*(self.LOCK.format(user_id) for user_id in locked_user_ids))

    def _retrain_enqueue_job(self, job: RetrainUserEmbeddingJob):
        job_id = self.redis.incr(self.COUNTER)

        user_id = job.user_id

        data = job.model_dump()
        data['job_id'] = job_id

        self.redis.zadd(self.USER.format(user_id), {job_id: job_id})
        self.redis.hset(self.JOBS, job_id, json.dumps(data))

        is_oldest = self.redis.zscore(self.GLOBAL, user_id) is None

        if is_oldest:
            self.redis.zadd(self.GLOBAL, {user_id: job_id})

    def _retrain_get_jobs(self, user_id: int, limit: int = 50) -> list[RetrainUserEmbeddingJob]:
        data = self.redis.zrange(self.USER.format(user_id), 0, limit - 1, withscores=True)

        if not data:
            return []
        
        members, scores = zip(*data)

        job_ids = [int(score) for score in scores]
        
        raw_jobs = self.redis.hmget(self.JOBS, job_ids)
        jobs = [RetrainUserEmbeddingJob(**json.loads(raw_job)) for raw_job in raw_jobs if raw_job is not None]

        return jobs
    
    def _retrain_remove_jobs(self, jobs: list[RetrainUserEmbeddingJob]):
        if not jobs:
            return

        user_ids = list(set(job.user_id for job in jobs))

        pipe = self.redis.pipeline()
        
        for user_id, user_jobs in groupby(jobs, key=lambda job: job.user_id):
            job_ids = [job.job_id for job in user_jobs]
            
            pipe.zrem(self.USER.format(user_id), *job_ids)
            pipe.hdel(self.JOBS, *job_ids)

        pipe.execute()

        self.update_global_queue(user_ids)

    def _retrain_update_global_queue(self, user_ids: list[int]):
        pipe = self.redis.pipeline()

        for user_id in user_ids:
            user_oldest_job = self.redis.zrange(self.USER.format(user_id), 0, 0, withscores=True)

            if not user_oldest_job:
                pipe.zrem(self.GLOBAL, user_id)
                continue
            
            pipe.zadd(self.GLOBAL, {user_id: user_oldest_job[0][1]})

        pipe.execute()

    def _retrain_get_user_ids(self) -> list[int]:
        user_ids = self.redis.zrange(self.GLOBAL, 0, -1)

        if not user_ids:
            return []
        
        return [int(user_id) for user_id in user_ids]