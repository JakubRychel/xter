from .models import Bot
from .services import create_bot_embedding_request, score_thread_request

def create_bot_embedding(bot_id):
    personality = (
        Bot.objects.filter(id=bot_id)
        .values_list('personality_obj__description', flat=True)
        .first()
    )

    create_bot_embedding_request(bot_id, personality)

def score_thread(bot_id, post_id):
    score = score_thread_request(bot_id, post_id)

    return score