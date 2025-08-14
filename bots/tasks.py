import random
import os
import time
from django.contrib.auth import get_user_model
from celery import shared_task
from transformers import pipeline
from posts.models import Post
from recommendations.logic import get_recommended_posts

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

User = get_user_model()

API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash-lite')

classifier = pipeline('zero-shot-classification', model='MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli')

def generate_text(prompt):
    retries = 3

    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted:
            wait_time = 2 ** attempt
            print(f'Przekroczony limit API, ponawianie próby za {wait_time} sekund...')
            time.sleep(wait_time)

    return None

def generate_post(username, displayed_name, personality):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    prompt = f'''
        Jesteś użytkownikiem portalu Xter podobnego do Twittera.

        Twoja nazwa użytkownika: {username}
        Twoja nazwa: {displayed_name}
        Twoja osobowość: {personality}

        Napisz jedno-, dwu- lub trzyzdaniowy post, który jest zgodny z Twoją osobowością:
    '''

    post = generate_text(prompt)

    if post is not None:
        return post

def generate_reply(username, displayed_name, personality, post, thread):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    prompt = f'''
        Jesteś użytkownikiem portalu Xter podobnego do Twittera.

        Twoja nazwa użytkownika: {username}
        Twoja nazwa: {displayed_name}
        Twoja osobowość: {personality}

        Cały wątek dla kontekstu: {thread}
        Każdy kolejny post wątku jest odpowiedzią na poprzedni post.
        Oto post na który odpowiadasz, odpowiedz tylko na niego z uwzględnieniem kontekstu wątku jeśli jest to potrzebne: {post}

        Napisz jedno-, dwu- lub trzyzdaniową odpowiedź, która jest zgodna z Twoją osobowością:
    '''

    reply = generate_text(prompt)

    if reply is not None:
        return reply

def get_thread_alignment(thread, personality):
    """
    Funckja zwraca słownik 'result' gdzie w 'result.scores' jest lista trzech wartości odpowiadających etykietom
    """
    input_text = f'''
        This is a conversation thread from a social media platform:

        {thread}

        The personality description of the user is as follows:
        {personality}
    '''

    result = classifier(
        input_text,
        candidate_labels=['matches', 'does not match', 'is neutral towards'],
        hypothesis_template = 'The thread content {} the style, interests, and personality of the user.',
        truncation = True,
        max_length = 512
    )

    return result

def get_thread_content(post):
    def stringify_post(post):
        return f'''
            Autor: {post.author.displayed_name} (@{post.author.username})
            Data publikacji: {post.published_at.strftime('%d %b %Y, %H:%M')}
            Treść: {post.content}
        '''
    
    thread = stringify_post(post)

    while post.parent is not None:
        post = post.parent
        thread = stringify_post(post) + '\n' + thread

    return thread

@shared_task
def run_bot(id):
    bot = User.objects.get(id=id)
    posts = get_recommended_posts(bot)

    for post in posts:
        post.readed_by.add(bot)

        thread_content = get_thread_content(post)

        alignment = get_thread_alignment(thread_content, bot.bot.personality)

        if (alignment['scores'][0] > 0.5):
            if alignment['scores'][0] + random.random() > 1.3:
                post.liked_by.add(bot)
            if alignment['scores'][0] + random.random() > 1.5:
                content = generate_reply(bot.username, bot.displayed_name, bot.bot.personality, post.content, thread_content)

                if content is not None:
                    Post.objects.create(author=bot, content=content, parent=post)

        if (alignment['scores'][1] > 0.5):
            if alignment['scores'][1] + random.random() > 1.8:
                content = generate_reply(bot.username, bot.displayed_name, bot.bot.personality, post.content, thread_content)

                if content is not None:
                    Post.objects.create(author=bot, content=content, parent=post)