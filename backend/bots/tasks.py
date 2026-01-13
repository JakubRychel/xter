import random
from functools import wraps
from celery import shared_task
from .queue import *


BOT_TASKS = {}


"""
SCHEMATY GENEROWANIA ZADAŃ DLA BOTÓW
"""

def generate_bot_task(bot_id, task_type=None):
    from .models import Bot

    mode = Bot.objects.filter(id=bot_id).values_list('mode', flat=True).first()

    BOT_BEHAVIOR = {
        'active': {
            'read_feed': 0.7,
            'write_post': 0.1,
            'set_mode_standby': 0.19,
            'set_mode_inactive': 0.01
        },
        'standby': {
            'sleep': 0.8,
            'set_mode_active': 0.19,
            'set_mode_inactive': 0.01
        },
        'inactive': {
            'set_mode_active': 0.4,
            'set_mode_standby': 0.6
        }
    }

    config = BOT_BEHAVIOR.get(mode, {})

    actions = list(config.keys())
    weights = list(config.values())

    if not task_type:
        task_type = random.choices(actions, weights=weights, k=1)[0]

    item = {
        'type': task_type
    }

    if task_type == 'read_feed':
        limit = random.randint(5, 25)
        item['payload'] = {'limit': limit}

    elif task_type == 'sleep':
        if mode == Bot.INACTIVE:
            countdown = random.randint(60*60*5, 60*60*8)
        else:
            countdown = random.randint(300, 1800)

        item['countdown'] = countdown

    elif task_type == 'set_mode_active':
        item['payload'] = {'mode': Bot.ACTIVE}

    elif task_type == 'set_mode_standby':
        item['payload'] = {'mode': Bot.STANDBY}

    elif task_type == 'set_mode_inactive':
        item['payload'] = {'mode': Bot.INACTIVE}
        item['next_task_type'] = 'sleep'

    return item

def plan_next_task(bot_id, task_type=None):
    from .queue import pop_bot_task

    next_task = pop_bot_task(bot_id) or generate_bot_task(bot_id, task_type=task_type)

    action = BOT_TASKS.get(next_task['type'])

    if not action:
        raise KeyError(f'Bot action "{next_task["type"]}" not found')

    payload = next_task.get('payload', {})
    countdown = next_task.get('countdown', 5)

    action.apply_async(
        args=(bot_id, payload),
        kwargs={'next_task_type': next_task.get('next_task_type', None)},
        countdown=countdown
    )


"""
DEFINICJA DEKORATORA ZADAŃ BOTÓW
"""

def bot_action(queue='tasks.low'):
    def decorator(fn):
        @shared_task(
            queue=queue,
            retry_for=(Exception,),
            retry_kwargs={'max_retries': 3, 'countdown': 30})
        @wraps(fn)
        def wrapper(bot_id, *args, **kwargs):
            from .models import Bot

            if not Bot.objects.filter(id=bot_id, enabled=True).exists():
                return
            
            next_task_type = kwargs.pop('next_task_type', None)

            try:
                fn(bot_id, *args)
            except Exception as e:
                print(f'Error in bot {bot_id} action {fn.__name__}: {e}')
            finally:
                plan_next_task(bot_id, task_type=next_task_type)

        return wrapper
    return decorator


"""
DZIAŁANIA BOTÓW
"""

@bot_action()
def sleep(bot_id, *args, **kwargs):
    print(f'Bot {bot_id} is sleeping...')

@bot_action()
def read_feed(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is reading feed...')

    from recommendations.logic import get_recommended_posts
    from .models import Bot

    bot_user = Bot.objects.get(id=bot_id).user
    limit = payload.get('limit', 10)

    post_ids = get_recommended_posts(bot_user).exclude(read_by=bot_user, author=bot_user).values_list('id', flat=True)[:limit]

    for post_id in post_ids:
        push_bot_task(bot_id, 'read_post', {'post_id': post_id})

@bot_action()
def read_post(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is reading post {payload.get("post_id")}...')

    from posts.models import Post
    from .models import Bot
    from .utils import get_thread_alignment

    post_id = payload.get('post_id')
    post = Post.objects.get(id=post_id)
    bot = Bot.objects.get(id=bot_id)

    post.read_by.add(bot.user_id)

    alignment = get_thread_alignment(post, bot.personality_obj)

    if (alignment > 0.5):
        if alignment + random.random() > 1.3:
            push_bot_task(bot_id, 'like_post', {'post_id': post_id})
        if alignment + random.random() > 1.5:
            push_bot_task(bot_id, 'reply_to_post', {'post_id': post_id})

@bot_action()
def write_post(bot_id, payload, *args, **kwargs):
    post_id = payload.get('post_id', None)

    if post_id is not None:
        print(f'Bot {bot_id} is replying to post {post_id}...')
    else:
        print(f'Bot {bot_id} is writing a post...')

    from posts.models import Post
    from .models import Bot
    from .utils import generate_post, generate_reply

    bot = Bot.objects.select_related('user').get(id=bot_id)

    post = Post.objects.get(id=post_id) if post_id else None

    try:
        content = generate_reply(bot, post) if post_id else generate_post(bot)

        if content is not None:
            Post.objects.create(author=bot.user, content=content, parent=post)

    except Exception as e:
        print(f'Error generating post/reply for bot {bot_id}: {e}')

@bot_action()
def like_post(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is liking post {payload.get("post_id")}...')

    from posts.models import Post
    from .models import Bot

    bot = Bot.objects.get(id=bot_id)

    post_id = payload.get('post_id')
    post = Post.objects.get(id=post_id)

    post.liked_by.add(bot.user_id)

@bot_action(queue='tasks.high')
def handle_notification(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is handling notification {payload.get("notification_id")}...')

    from notifications.models import Notification

    notification_id = payload.get('notification_id')
    notification = Notification.objects.get(id=notification_id)

    if notification.notification_type in [Notification.REPLY, Notification.MENTION, Notification.FOLLOWED_USER_POSTED]:
        related_post = notification.related_post

        push_bot_task(bot_id, 'read_post', {'post_id': related_post.id})

    elif notification.notification_type == Notification.LIKE:
        pass
    elif notification.notification_type == Notification.FOLLOW:
        pass

    notification.events.filter(seen=False).update(seen=True)

@bot_action()
def set_mode(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is setting mode to {payload.get("mode")}...')

    from .models import Bot

    mode = payload.get('mode')

    Bot.objects.filter(id=bot_id).update(mode=mode)


"""
REJESTRACJA DZIAŁAŃ BOTÓW
"""

BOT_TASKS.update({
    'sleep': sleep,
    'read_feed': read_feed,
    'read_post': read_post,
    'write_post': write_post,
    'reply_to_post': write_post,
    'like_post': like_post,
    'handle_notification': handle_notification,
    'set_mode_active': set_mode,
    'set_mode_standby': set_mode,
    'set_mode_inactive': set_mode,
})


"""
ZADANIA GENEROWANIA EMBEDDINGÓW
"""

@shared_task
def generate_personality_embedding(personality_id):
    from .models import Personality
    from recommendations.utils import get_text_embedding

    queryset = Personality.objects.filter(pk=personality_id)
    if not queryset.exists():
        return
    
    description = queryset.values_list('description', flat=True).first()

    embedding = get_text_embedding(description)

    queryset.update(embedding=embedding)