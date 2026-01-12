from redis import Redis
from django.conf import settings
import json

REDIS = Redis.from_url(settings.CELERY_BROKER_URL)

HIGH_QUEUE = 'bot:{bot_id}:high'
LOW_QUEUE = 'bot:{bot_id}:low'

def clear_bot_tasks(*bot_ids: int):
    for bot_id in bot_ids:
        REDIS.delete(
            HIGH_QUEUE.format(bot_id=bot_id),
            LOW_QUEUE.format(bot_id=bot_id)
        )

def pop_bot_task(bot_id):
    high_queue = HIGH_QUEUE.format(bot_id=bot_id)
    low_queue = LOW_QUEUE.format(bot_id=bot_id)

    raw = REDIS.rpop(high_queue) or REDIS.rpop(low_queue)

    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return None
        
    return None

def push_bot_task(bot_id, task_type, payload, priority='low', **kwargs):
    data = {
        'type': task_type,
        'payload': payload or {},
        'next_task_type': kwargs.get('next_task_type', None)
    }

    if 'countdown' in kwargs and kwargs['countdown'] is not None:
        data['countdown'] = kwargs['countdown']

    item = json.dumps(data)

    queue = HIGH_QUEUE.format(bot_id=bot_id) if priority == 'high' else LOW_QUEUE.format(bot_id=bot_id)

    REDIS.lpush(queue, item)