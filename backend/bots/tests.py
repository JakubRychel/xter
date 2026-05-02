import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model

from .tasks import generate_bot_task, plan_next_task, BOT_TASKS
from .models import Bot

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