from django_redis import get_redis_connection
from redis.asyncio import Redis

def get_redis():
    return get_redis_connection('default')

def get_aredis():
    redis = Redis(
        host='redis',
        port='6379',
        db=1,
        decode_responses=True
    )

    return redis