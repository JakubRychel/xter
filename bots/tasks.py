import random
from functools import wraps
from celery import shared_task


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
            'set_mode_standby': 0.199,
            'set_mode_inactive': 0.001
        },
        'standby': {
            'sleep': 0.8,
            'set_mode_active': 0.199,
            'set_mode_inactive': 0.001
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
        if mode == Bot.STANDBY:
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

            fn(bot_id, *args)

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

@bot_action()
def write_post(bot_id, *args, **kwargs):
    print(f'Bot {bot_id} is writing a post...')

@bot_action()
def reply_to_post(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is replying to post {payload.get("post_id")}...')

@bot_action()
def like_post(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is liking post {payload.get("post_id")}...')

@bot_action(queue='tasks.high')
def handle_notification(bot_id, payload, *args, **kwargs):
    print(f'Bot {bot_id} is handling notification {payload.get("notification_id")}...')

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
    'write_post': write_post,
    'reply_to_post': reply_to_post,
    'like_post': like_post,
    'handle_notification': handle_notification,
    'set_mode_active': set_mode,
    'set_mode_standby': set_mode,
    'set_mode_inactive': set_mode,
})


# @shared_task
# def generate_personality_embedding(personality_id):
#     from .models import Personality
#     from recommendations.utils import get_text_embedding

#     queryset = Personality.objects.filter(pk=personality_id)
#     if not queryset.exists():
#         return
    
#     description = queryset.values_list('description', flat=True).first()

#     embedding = get_text_embedding(description)

#     queryset.update(embedding=embedding)

# @shared_task(bind=True, max_retries=3)
# def read_post(self, post_id, bot_id):
#     from .utils import get_thread_alignment, get_thread_content, generate_reply
#     from posts.models import Post
#     from django.contrib.auth import get_user_model
#     from google.api_core.exceptions import ResourceExhausted

#     User = get_user_model()

#     post = Post.objects.get(id=post_id)
#     bot = User.objects.get(id=bot_id)

#     post.readed_by.add(bot)
#     thread_content = get_thread_content(post)

#     alignment = get_thread_alignment(thread_content, bot.bot.personality)

#     try:
#         if (alignment['scores'][0] > 0.5):
#             if alignment['scores'][0] + random.random() > 1.3:
#                 post.liked_by.add(bot)
#             if alignment['scores'][0] + random.random() > 1.5:
#                 content = generate_reply(bot.username, bot.displayed_name, bot.bot.personality, post.content, thread_content)

#                 if content is not None:
#                     Post.objects.create(author=bot, content=content, parent=post)

#         if (alignment['scores'][1] > 0.5):
#             if alignment['scores'][1] + random.random() > 1.8:
#                 content = generate_reply(bot.username, bot.displayed_name, bot.bot.personality, post.content, thread_content)

#                 if content is not None:
#                     Post.objects.create(author=bot, content=content, parent=post)
#     except ResourceExhausted:
#         countdown = 2 ** self.request.retries
#         raise self.retry(countdown=countdown, exc=ResourceExhausted('Google API quota exceeded, retrying...'))

# @shared_task(bind=True, max_retries=3)
# def write_post(self, bot_id):
#     from .utils import generate_post
#     from posts.models import Post
#     from django.contrib.auth import get_user_model
#     from google.api_core.exceptions import ResourceExhausted

#     User = get_user_model()

#     bot = User.objects.get(id=bot_id)

#     try:
#         content = generate_post(bot.username, bot.displayed_name, bot.bot.personality)

#         if content is not None:
#             Post.objects.create(author=bot, content=content)
#     except ResourceExhausted:
#         countdown = 2 ** self.request.retries
#         raise self.retry(countdown=countdown, exc=ResourceExhausted('Google API quota exceeded, retrying...'))

# @shared_task
# def run_bot(id):
#     from recommendations.logic import get_recommended_posts
#     from django.contrib.auth import get_user_model

#     User = get_user_model()

#     bot = User.objects.get(id=id)
#     recommended_posts = get_recommended_posts(bot)
#     posts = recommended_posts.exclude(readed_by=bot, author=bot)

#     if random.random() < 0.1: write_post.delay(bot.id)

#     for post in posts:
#         read_post.delay(post.id, bot.id)