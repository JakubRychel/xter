import os
import numpy as np
from .services import generate_text_request, chat_request


def get_thread_posts(post):
    posts = [post]

    while post.parent is not None:
        post = post.parent
        posts.append(post)

    return list(reversed(posts))

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    
    return np.dot(a, b) / denom

def stringify_post(post):
    return f'''
        Autor: {post.author.displayed_name} (@{post.author.username})
        Data publikacji: {post.published_at.strftime('%d %b %Y, %H:%M')}
        Treść: {post.content}
    '''

def build_thread(bot, post, thread=None):
    if thread is None:
        thread = []

    post = post.parent

    if post is not None:
        build_thread(bot, post, thread)

        role = 'model' if post.author == bot.user else 'user'
        
        if thread and thread[-1]['role'] == role:
            thread[-1]['parts'].append(stringify_post(post))
        else:
            thread.append({
                'role': role,
                'parts': [stringify_post(post)]
            })

    return thread

def generate_post(username, displayed_name, personality):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    system_instruction = f'''
        Jesteś użytkownikiem portalu Xter podobnego do X/Twittera.

        Twoja nazwa użytkownika: {username}
        Twoja nazwa: {displayed_name}
        Twoja osobowość: {personality}
    '''

    contents = 'Napisz jedno-, dwu- lub trzyzdaniowy post, który jest zgodny z Twoją osobowością. Wygeneruj wyłącznie treść posta bez żadnych dodatkowych informacji. Nie zawieraj informacji takich jak data lub nazwa użytkownika bota.'

    response = generate_text_request(
        system_instruction=system_instruction,
        contents=contents
    )

    return response or None

def generate_reply(username, displayed_name, personality, message, thread):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    system_instruction = f'''
        Jesteś użytkownikiem portalu Xter podobnego do X/Twittera.

        Twoja nazwa użytkownika: {username}
        Twoja nazwa: {displayed_name}
        Twoja osobowość: {personality}

        Udzielasz jedno-, dwu- lub trzyzdaniowej odpowiedzi, która jest zgodna z Twoją osobowością. Wygeneruj wyłącznie treść odpowiedzi bez żadnych dodatkowych informacji. Nie zawieraj informacji takich jak data lub nazwa użytkownika bota.
    '''

    response = chat_request(
        system_instruction=system_instruction,
        history=thread,
        message=message
    )

    return response or None