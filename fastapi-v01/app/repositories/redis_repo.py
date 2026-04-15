import json
from contextlib import contextmanager
from app.core.redis import redis_client
from fastapi.app.jobs.embed_post_job import EmbedPostJob
from fastapi.app.jobs.retrain_user_embedding_job import RetrainUserJob

class RedisRepo:
    RETRAIN_LOCK = 'retrain:lock:{}'
    RETRAIN_GLOBAL = 'retrain:global'
    RETRAIN_USER = 'retrain:user:{}'
    RETRAIN_JOB = 'retrain:job:{}'
    RETRAIN_JOB_ID = 'retrain:job:id'

    GENERATE_LOCK = 'lock:generate'
    GENERATE_QUEUE = 'queue:generate:posts'
    GENERATE_SET = 'set:generate:posts:queued'

    def __init__(self):
        self.redis = redis_client


    class UserBusy(Exception):
        pass

    """
    EMBEDDINGI POSTÓW
    """

    def is_post_queued(self, post_id):
        return self.redis.sismember(self.GENERATE_SET, post_id)

    def create_generate_post_embeddings_job(self, post_id: int, post_content: str, thread_content: str):
        job = {
            'post_id': post_id,
            'post_content': post_content,
            'thread_content': thread_content
        }

        return job
    
    def enqueue_generate_post_embeddings_job(self, post_id: int, post_content: str, thread_content: str):
        job = self.create_generate_post_embeddings_job(post_id, post_content, thread_content)

        if self.redis.sadd(self.GENERATE_SET, post_id):
            self.redis.rpush(self.GENERATE_QUEUE, json.dumps(job))

    def build_generate_post_embeddings_batch(self, jobs: list, limit: int = 50):
        if not jobs:
            jobs = []

        raw_jobs = self.redis.lpop(self.GENERATE_QUEUE, limit)

        if raw_jobs:
            jobs.extend(json.loads(job) for job in raw_jobs)
        
            post_ids = [job['post_id'] for job in jobs]
            self.redis.srem(self.GENERATE_SET, *post_ids)
        
        return jobs

    @contextmanager
    def post_embeddings_generating_lock(self, expire: int = 5):
        acquired = self.redis.set(self.GENERATE_LOCK, 1, nx=True, ex=expire)

        if not acquired:
            yield False
        else:
            try:
                yield True
            finally:
                self.redis.delete(self.GENERATE_LOCK)


    """
    EMBEDDINGI UŻYTKOWNIKÓW
    """

    def is_retrain_user_embedding_queue_empty(self, user_id: int) -> bool:
        return self.redis.zcard(self.RETRAIN_READY.format(user_id)) == 0

    def update_global_user_priority(self, user_id: int):
        earliest_job = self.redis.zrange(self.RETRAIN_READY.format(user_id), 0, 0, withscores=True)

        if earliest_job:
            score = earliest_job[0][1]
            self.redis.zadd(self.RETRAIN_GLOBAL, {user_id: score})
        else:
            self.redis.zrem(self.RETRAIN_GLOBAL, user_id)

    def create_retrain_user_embedding_job(self, user_id: int, post_id: int, alpha: float):
        sec, micro = self.redis.time()
        timestamp = sec + micro / 1_000_000

        job = {
            'user_id': user_id,
            'post_id': post_id,
            'alpha': alpha,
            'timestamp': timestamp
        }

        return job

    def enqueue_retrain_user_embedding_job(self, user_id: int, post_id: int, alpha: float):
        job = self.create_retrain_user_embedding_job(user_id, post_id, alpha)

        is_empty = self.is_retrain_user_embedding_queue_empty(user_id)

        self.redis.zadd(self.RETRAIN_READY.format(user_id), {json.dumps(job): job.get('timestamp')})

        if is_empty:
            with self.user_embeddings_retraining_lock(user_id) as locked:
                if locked:
                    self.update_global_user_priority(user_id)

    ########################

    def lock_user(self, user_id: int, expire: int = 60) -> bool:
        locked = self.redis.set(self.RETRAIN_LOCK.format(user_id), 1, nx=True, ex=expire)

        if locked:
            self.redis.zrem(self.RETRAIN_GLOBAL, user_id)

        return bool(locked)
    
    def unlock_users(self, user_ids: list[int]):
        self.redis.delete(*(self.RETRAIN_LOCK.format(user_id) for user_id in user_ids))

        for user_id in user_ids:
            user_oldest_job = self.redis.zrange(self.RETRAIN_READY.format(user_id), 0, 0, withscores=True)

            if not user_oldest_job:
                continue
            
            self.redis.zadd(self.RETRAIN_GLOBAL, {user_id: user_oldest_job[0][1]})

    def get_next_user_id(self) -> int | None:
        user_list = self.redis.zrange(self.RETRAIN_GLOBAL, 0, 0)

        if not user_list:
            return None
        
        user_id = int(user_list[0])

        return user_id

    def get_job_ids(self, user_id: int, limit: int) -> list[int]:
        job_ids = self.redis.zrange(self.RETRAIN_USER.format(user_id), 0, limit - 1)

        return [int(job_id) for job_id in job_ids]

    def pop_jobs(self, job_ids: list[int]) -> list[RetrainUserJob]:
        pipeline = self.redis.pipeline()

        pipeline.zrem(self.RETRAIN_GLOBAL, )