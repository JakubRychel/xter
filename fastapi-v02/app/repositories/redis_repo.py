from contextlib import contextmanager
import json

from app.core.exceptions import EmbeddingBusy, NoJobsToProcess, UserBusy
from app.core.redis import redis_client
from typing import ClassVar


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

        if namespace == 'embed':
            self.COUNTER = 'embed:counter'
            self.JOBS = 'embed:jobs'
            self.QUEUE = 'embed:queue'
            self.LOCK = 'embed:lock'

            self.lock = self._embed_lock
            self.enqueue_job = self._embed_enqueue_job
            self.get_jobs = self._embed_get_jobs
            self.remove_jobs = self._embed_remove_jobs
        
        elif namespace == 'retrain':
            self.COUNTER = 'retrain:counter' #bieżące id joba
            self.JOBS = 'retrain:jobs' #przechowuje payloady jobów według id
            self.GLOBAL = 'retrain:global' #przechowuje id najstarszego joba per user
            self.USER = 'retrain:user:{}' #kolejka FIFO id jobów per user
            self.LOCK = 'retrain:lock:{}' #lock per user

            self.lock = self._retrain_lock
            self.lock_user = self._retrain_lock_user
            self.unlock_users = self._retrain_unlock_users
            self.get_user_ids = self._retrain_get_user_ids
            self.get_next_user_id = self._retrain_get_next_user_id
            self.enqueue_job = self._retrain_enqueue_job
            self.get_jobs = self._retrain_get_jobs
            self.remove_jobs = self._retrain_remove_jobs


    def is_post_queued(self, post_id: int) -> bool:
        return self.redis.zscore('embed:queue', post_id) is not None
    

    @contextmanager
    def _embed_lock(self, expire: int = 60):
        def acquire() -> bool:
            acquired = self.redis.set(self.LOCK, 1, nx=True, ex=expire)
            return acquired
        
        try:
            yield acquire

        finally:
            self.redis.delete(self.LOCK)

    def _embed_enqueue_job(self, payload: dict):
        job_id = self.redis.incr(self.COUNTER)

        post_id = payload.get('post_id')

        old_job_id = self.redis.zscore(self.QUEUE, post_id)

        self.redis.zadd(self.QUEUE, {post_id: job_id})
        self.redis.hset(self.JOBS, job_id, json.dumps({
            'job_id': job_id,
            'payload': payload
        }))

        if old_job_id is not None:
            self.redis.hdel(self.JOBS, int(old_job_id))

    def _embed_get_jobs(self, limit: int = 50) -> list[dict]:
        data = self.redis.zrange(self.QUEUE, 0, limit - 1, withscores=True)

        if not data:
            return []
        
        members, scores = zip(*data)

        job_ids = [int(score) for score in scores]
        
        raw_jobs = self.redis.hmget(self.JOBS, job_ids)
        jobs = [json.loads(raw_job) for raw_job in raw_jobs if raw_job is not None]

        return jobs
    
    def _embed_remove_jobs(self, job_ids: list[int]):
        if not job_ids:
            return

        self.redis.zremrangebyscore(self.QUEUE, min(job_ids), max(job_ids))
        self.redis.hdel(self.JOBS, *job_ids)


    @contextmanager
    def _retrain_lock(self):
        locked_user_ids = set()

        def acquire(user_id: int):
            acquired = self.lock_user(user_id)
                
            if acquired:
                locked_user_ids.add(user_id)

            return acquired
        
        def acquire_next_user():
            user_ids = self.get_user_ids()

            if not user_ids:
                return None

            for user_id in user_ids:
                acquired = acquire(user_id)

                if acquired:
                    return user_id

            #return acquire_next_user()

        try:
            yield acquire, acquire_next_user
    
        finally:
            self.unlock_users(locked_user_ids)

    def _retrain_lock_user(self, user_id: int, expire: int = 60) -> bool:
        locked = self.redis.set(self.LOCK.format(user_id), 1, nx=True, ex=expire)

        # if locked:
        #     self.redis.zrem(self.GLOBAL, user_id)

        return locked
    
    def _retrain_unlock_users(self, user_ids: set[int]):
        self.redis.delete(*(self.LOCK.format(user_id) for user_id in user_ids))

        # for user_id in user_ids:
        #     user_oldest_job = self.redis.zrange(self.READY.format(user_id), 0, 0, withscores=True)

        #     if not user_oldest_job:
        #         continue
            
        #     self.redis.zadd(self.GLOBAL, {user_id: user_oldest_job[0][1]})

    def _retrain_enqueue_job(self, payload: dict):
        job_id = self.redis.incr(self.COUNTER)

        user_id = payload.get('user_id')

        self.redis.zadd(self.USER.format(user_id), {job_id: job_id})
        self.redis.hset(self.JOBS, job_id, json.dumps({
            'job_id': job_id,
            'payload': payload
        }))

        is_oldest = self.redis.zscore(self.GLOBAL, user_id) is None

        if is_oldest:
            self.redis.zadd(self.GLOBAL, {user_id: job_id})

        return True, job_id
    
    def _retrain_get_jobs(self, user_id: int, limit: int = 50) -> list[dict]:
        data = self.redis.zrange(self.USER.format(user_id), 0, limit - 1, withscores=True)

        if not data:
            return []
        
        members, scores = zip(*data)

        job_ids = [int(score) for score in scores]
        
        raw_jobs = self.redis.hmget(self.JOBS, job_ids)
        jobs = [json.loads(raw_job) for raw_job in raw_jobs if raw_job is not None]

        return jobs

    def _retrain_remove_jobs(self, job_ids: list[int]):
        if not job_ids:
            return

        pipe = self.redis.pipeline()

        for job_id in job_ids:
            raw_job = self.redis.hget(self.JOBS, job_id)

            if not raw_job:
                continue
            
            job = json.loads(raw_job)
            user_id = job['payload']['user_id']

            pipe.zrem(self.USER.format(user_id), job_id)
            pipe.hdel(self.JOBS, job_id)

        pipe.execute()

    def _retrain_get_user_ids(self):
        users = self.redis.zrange(self.GLOBAL, 0, -1)

        if not users:
            return []
        
        return users

    def _retrain_get_next_user_id(self) -> int | None:
        user_list = self.redis.zrange(self.GLOBAL, 0, 0)

        if not user_list:
            raise NoJobsToProcess()
        
        user_id = int(user_list[0])

        return user_id