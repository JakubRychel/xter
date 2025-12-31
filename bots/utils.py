import os
import numpy as np
from google import genai
from recommendations.utils import get_or_create_post_embedding

GOOGLE_KEY = os.getenv('GOOGLE_API_KEY')
OPEN_ROUTER_KEY = os.getenv('OPEN_ROUTER_API_KEY')

def stringify_post(post):
    return f'''
        Autor: {post.author.displayed_name} (@{post.author.username})
        Data publikacji: {post.published_at.strftime('%d %b %Y, %H:%M')}
        Treść: {post.content}
    '''

def get_thread_content(post, bot):
    thread = []

    while post.parent is not None:
        post = post.parent
        thread.append({
            'role': 'assistant' if post.author == bot else 'user',
            'content': stringify_post(post)
        })

    return list(reversed(thread))

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

def get_thread_alignment(post, personality):
    posts = get_thread_posts(post)
    post_embeddings = [get_or_create_post_embedding(p) for p in posts]
    thread_embedding = np.mean(np.array(post_embeddings), axis=0).tolist()

    personality_embedding = personality.embedding

    alignment = (cosine_similarity(thread_embedding, personality_embedding) + 1) / 2

    return alignment

def generate_post(username, displayed_name, personality):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    system_instructions = f'''
        Jesteś użytkownikiem portalu Xter podobnego do X/Twittera.

        Twoja nazwa użytkownika: {username}
        Twoja nazwa: {displayed_name}
        Twoja osobowość: {personality}

        Napisz jedno-, dwu- lub trzyzdaniowy post, który jest zgodny z Twoją osobowością. Wygeneruj jedynie treść bez żadnych dodatkowych informacji.
    '''

    client = genai.Client()

    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=system_instructions
    )

    return response.text or None

def generate_reply(username, displayed_name, personality, post, thread):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    system_instructions = f'''
        Jesteś użytkownikiem portalu Xter podobnego do X/Twittera.

        Twoja nazwa użytkownika: {username}
        Twoja nazwa: {displayed_name}
        Twoja osobowość: {personality}

        Napisz jedno-, dwu- lub trzyzdaniową odpowiedź, która jest zgodna z Twoją osobowością. Wygeneruj jedynie treść bez żadnych dodatkowych informacji.
    '''

    messages = [{
        'role': 'system',
        'content': system_instructions
    }]

    messages.extend(thread)

    client = genai.Client()
    chat = client.chats.create(model='gemini-2.5-flash-lite', history=messages)

    response = chat.send_message(post)

    return response.text or None