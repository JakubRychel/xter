import os
import numpy as np
import google.generativeai as genai
from recommendations.utils import get_or_create_post_embedding

GOOGLE_KEY = os.getenv('GOOGLE_API_KEY')
OPEN_ROUTER_KEY = os.getenv('OPEN_ROUTER_API_KEY')

genai.configure(api_key=GOOGLE_KEY)

model = genai.GenerativeModel('gemini-2.5-flash-lite')

# from transformers import pipeline
# classifier = pipeline('zero-shot-classification', model='MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli')

# def get_thread_alignment(thread, personality):
#     """
#     Funckja zwraca słownik 'result' gdzie w 'result.scores' jest lista trzech wartości odpowiadających etykietom
#     """
#     input_text = f'''
#         This is a conversation thread from a social media platform:

#         {thread}

#         The personality description of the user is as follows:
#         {personality}
#     '''

#     result = classifier(
#         input_text,
#         candidate_labels=['matches', 'does not match', 'is neutral towards'],
#         hypothesis_template = 'The thread content {} the style, interests, and personality of the user.',
#         truncation = True,
#         max_length = 512
#     )

#     return result

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

    prompt = f'''
        Jesteś użytkownikiem portalu Xter podobnego do Twittera.

        Twoja nazwa użytkownika: {username}
        Twoja nazwa: {displayed_name}
        Twoja osobowość: {personality}

        Napisz jedno-, dwu- lub trzyzdaniowy post, który jest zgodny z Twoją osobowością:
    '''

    post = model.generate_content(prompt)

    return post.text or None

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

    reply = model.generate_content(prompt)

    return reply.text or None