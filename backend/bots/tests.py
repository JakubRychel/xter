import json
import pytest
from unittest.mock import patch, call
from django.contrib.auth import get_user_model

from posts.models import Post
from .tasks import generate_bot_task, plan_next_task, BOT_TASKS
from .models import Bot
from .queue import pop_bot_task

User = get_user_model()


# docker compose exec backend pytest bots/tests.py -v


class FakeRandom:
    def choices(self, *args, **kwargs):
        return ['read_feed']
    
    def randint(self, a, b):
        return 10


@pytest.fixture
def bot(db):
    user = User.objects.create()
    bot = Bot.objects.create(user=user, mode='active', enabled=True)

    return bot


@pytest.mark.django_db
def test_generate_read_feed_task(bot):
    task = generate_bot_task(bot.id, task_type='read_feed')

    assert task['type'] == 'read_feed'
    assert 5 <= task['payload']['limit'] <= 25

@pytest.mark.django_db
def test_generate_task_with_rng(bot):
    task = generate_bot_task(bot.id, rng=FakeRandom())

    assert task['type'] == 'read_feed'
    assert task['payload']['limit'] == 10

@pytest.mark.django_db
@patch('bots.queue.pop_bot_task')
def test_plan_next_task_uses_queue(mock_pop, bot):
    mock_pop.return_value = {'type': 'sleep', 'payload': {}, 'countdown': 1}

    with patch.object(BOT_TASKS['sleep'], 'apply_async') as mock_async:
        plan_next_task(bot.id)

        mock_async.assert_called_once()

@pytest.mark.django_db
def test_set_mode_inactive_sets_next_sleep(bot):
    task = generate_bot_task(bot.id, task_type='set_mode_inactive')

    assert task['type'] == 'set_mode_inactive'
    assert task['payload']['mode'] == 'inactive'
    assert task['next_task_type'] == 'sleep'

@pytest.mark.django_db
@patch('bots.queue.pop_bot_task')
def test_set_mode_inactive_schedules_sleep(mock_pop, bot):
    mock_pop.return_value = {
        'type': 'set_mode_inactive',
        'payload': {'mode': 'inactive'},
        'next_task_type': 'sleep',
        'countdown': 1
    }

    with patch.object(BOT_TASKS['set_mode_inactive'], 'apply_async') as mock_async:
        plan_next_task(bot.id)

        mock_async.assert_called_once()

        _, kwargs = mock_async.call_args

        assert kwargs['kwargs']['next_task_type'] == 'sleep'

@pytest.mark.django_db
@patch('bots.queue.pop_bot_task')
@patch('bots.tasks.generate_bot_task')
def test_generate_task_when_queue_empty(mock_generate, mock_pop, bot):
    mock_pop.return_value = None
    mock_generate.return_value = {
        'type': 'sleep',
        'payload': {},
        'countdown': 2
    }

    with patch.object(BOT_TASKS['sleep'], 'apply_async') as mock_async:
        plan_next_task(bot.id)

        mock_generate.assert_called_once()
        mock_async.assert_called_once()

@pytest.mark.django_db
@patch('bots.queue.pop_bot_task')
def test_plan_next_task_unknown_action(mock_pop, bot):
    mock_pop.return_value = {'type': 'unknown_task'}

    with pytest.raises(KeyError):
        plan_next_task(bot.id)

@pytest.mark.django_db
def test_disabled_bot_does_not_execute(bot):
    bot.enabled = False
    bot.save()

    with patch('bots.tasks.plan_next_task') as mock_next:
        BOT_TASKS['sleep'](bot.id)

        mock_next.assert_not_called()

@pytest.mark.django_db
def test_read_post_marks_as_read(bot):
    post = Post.objects.create(author=bot.user, content='test')

    BOT_TASKS['read_post'](bot.id, {'post_id': post.id})

    assert bot.user in post.read_by.all()


class FakeRedis:
    def __init__(self):
        self.data = {}

    def rpop(self, key):
        queue = self.data.get(key, [])

        if queue:
            return queue.pop()
        
        return None


@pytest.mark.django_db
@patch('bots.queue.REDIS')
def test_pop_bot_task_prioritizes_high_queue(mock_redis, bot):
    fake = FakeRedis()

    high_key = f'bot:{bot.id}:high'
    low_key = f'bot:{bot.id}:low'

    fake.data[high_key] = [json.dumps({'type': 'high_task'}).encode()]
    fake.data[low_key] = [json.dumps({'type': 'low_task'}).encode()]

    mock_redis.rpop.side_effect = fake.rpop

    task = pop_bot_task(bot.id)

    assert task['type'] == 'high_task'

    assert fake.data[low_key] == [json.dumps({'type': 'low_task'}).encode()]

    assert mock_redis.rpop.call_args_list == [call(high_key)]

@pytest.mark.django_db
@patch('bots.queue.REDIS')
def test_pop_bot_task_fallback_to_low_queue(mock_redis, bot):
    fake = FakeRedis()

    high_key = f'bot:{bot.id}:high'
    low_key = f'bot:{bot.id}:low'

    fake.data[high_key] = []
    fake.data[low_key] = [json.dumps({'type': 'low_task'}).encode()]

    mock_redis.rpop.side_effect = fake.rpop

    task = pop_bot_task(bot.id)

    assert task['type'] == 'low_task'

    assert mock_redis.rpop.call_args_list == [
        call(high_key),
        call(low_key)
    ]