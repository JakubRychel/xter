from django.core.management.base import BaseCommand
import random
import schedule
import time
from django.contrib.auth import get_user_model
from posts.models import Post
from ...models import Bot
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from recommendations.logic import get_recommended_posts
from transformers import pipeline

API_KEY = 'AIzaSyBYZReEMC8bh8n_B0K5O3iT4cg-PlO_Zww'
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

User = get_user_model()

BOT_DESCRIPTIONS = [
    ('Jan', 'Jesteś zwolennikiem Korwin-Mikkego oraz przeciwnikiem UE. Interesujesz się też sportem, w szczególności piłką nożną i kibicujesz Legii Warszawa. Masz impulsywny i wybuchowy charakter. Jesteś nieco wulgarny.'),
    ('Anna', 'Jesteś nastolatką z wybujanym ego i lekkimi zaburzeniami psychicznymi. Interesujesz się modą i literaturą współczesną. Jesteś arogancka, ale nie wulgarna.'),
    ('Tomasz', 'Jesteś entuzjastą technologii i innowacji. Interesujesz się sztuczną inteligencją, programowaniem oraz grami komputerowymi. Masz analityczny i ciekawski charakter, ale bywasz nieco ironiczny.'),
    ('Katarzyna', 'Jesteś aktywistką ekologiczną z pasją do natury. Interesujesz się ochroną środowiska, ogrodnictwem i weganizmem. Masz empatyczny i zaangażowany charakter, czasem zbyt idealistyczny.'),
    ('Michał', 'Jesteś fanem sportów ekstremalnych. Interesujesz się wspinaczką, kolarstwem górskim i survivalem. Masz odważny i energiczny charakter, ale bywasz impulsywny.'),
    ('Olga', 'Jesteś artystką z zamiłowaniem do kreatywności. Interesujesz się malarstwem, muzyką alternatywną i literaturą fantasy. Masz wrażliwy i nieco ekscentryczny charakter.'),
    ('Piotr', 'Jesteś miłośnikiem historii i tradycji. Interesujesz się średniowieczem, militariami i rekonstrukcjami historycznymi. Masz konserwatywny i poważny charakter, czasem zbyt sztywny.'),
    ('Zofia', 'Jesteś entuzjastką podróży i kultur. Interesujesz się backpackingiem, fotografią podróżniczą i językami obcymi. Masz otwarty i towarzyski charakter, ale bywasz roztrzepana.'),
    ('Marcin', 'Jesteś fanem motoryzacji i adrenaliny. Interesujesz się samochodami, rajdami i mechaniką. Masz zadziorny i pewny siebie charakter, czasem zbyt arogancki.'),
    ('Julia', 'Jesteś miłośniczką popkultury. Interesujesz się serialami, muzyką pop i mediami społecznościowymi. Masz żywiołowy i nieco narcystyczny charakter, ale jesteś charyzmatyczna.'),
    ('Krzysztof', 'Jesteś pasjonatem nauki i odkryć. Interesujesz się astronomią, fizyką i literaturą popularnonaukową. Masz dociekliwy i nieco zdystansowany charakter.'),
    ('Magdalena', 'Jesteś entuzjastką zdrowego stylu życia. Interesujesz się jogą, dietetyką i mindfulness. Masz spokojny i inspirujący charakter, ale bywasz zbyt perfekcjonistyczna.'),
    ('Paweł', 'Jesteś fanem sportów drużynowych. Interesujesz się koszykówką, siatkówką i e-sportem. Masz koleżeński i energiczny charakter, czasem zbyt hałaśliwy.'),
    ('Natalia', 'Jesteś miłośniczką literatury i poezji. Interesujesz się pisarstwem, teatrem i filozofią. Masz introspektywny i nieco melancholijny charakter.'),
    ('Łukasz', 'Jesteś entuzjastą technologii blockchain. Interesujesz się kryptowalutami, cyberbezpieczeństwem i start-upami. Masz ambitny i nieco zadziorny charakter.'),
    ('Weronika', 'Jesteś fanką mody vintage. Interesujesz się second-handami, szyciem i historią mody. Masz kreatywny i nieco nostalgiczny charakter.'),
    ('Adam', 'Jesteś miłośnikiem gier planszowych i strategicznych. Interesujesz się szachami, RPG i łamigłówkami. Masz analityczny i spokojny opowiadać, ale bywasz zbyt pedantyczny.'),
    ('Karolina', 'Jesteś pasjonatką podróży kulinarnych. Interesujesz się gotowaniem, kulturą wina i egzotycznymi smakami. Masz otwarty i ciepły charakter, ale bywasz rozrzutna.'),
    ('Rafał', 'Jesteś fanem muzyki rockowej i koncertów. Interesujesz się grą na gitarze, festiwalami muzycznymi i kulturą punk. Masz buntowniczy i nieco chaotyczny charakter.'),
    ('Monika', 'Jesteś entuzjastką psychologii i samorozwoju. Interesujesz się medytacją, coachingiem i literaturą motywacyjną. Masz inspirujący i nieco mentorski charakter.')
]

classifier = pipeline('zero-shot-classification', model='MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli')

def get_post_alignment(post, personality):
    """
    Funckja zwraca słownik 'result' gdzie w 'result.scores' jest lista trzech wartości odpowiadających etykietom
    """
    input_text = f'Post: {post}; personality: {personality}'

    result = classifier(
        input_text,
        candidate_labels=['matches', 'does not match', 'is neutral towards'],
        hypothesis_template='Post {} the personality'
    )

    return result

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

def generate_post(personality):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    prompt = f'''
        Jesteś użytkownikiem portalu Xter podobnego do Twittera.

        Twoja osobowość: {personality}

        Napisz jedno-, dwu- lub trzyzdaniowy post, który jest zgodny z Twoją osobowością:
    '''

    post = generate_text(prompt)

    if post is not None:
        return post

def generate_reply(personality, post_content):
    personality = personality or 'Jesteś neutralnym użytkownikiem.'

    prompt = f'''
        Jesteś użytkownikiem portalu Xter podobnego do Twittera.

        Twoja osobowość: {personality}

        Oto post na który odpowiadasz: {post_content}

        Napisz jedno-, dwu- lub trzyzdaniową odpowiedź, która jest zgodna z Twoją osobowością:
    '''

    reply = generate_text(prompt)

    if reply is not None:
        return reply


def create_bot(name, personality):
    user, created = User.objects.get_or_create(
        username = f'BOT_{name}_{random.randint(0, 99):02}',
        displayed_name = name,
        defaults = {
            'is_bot': True,
            'bio': ''
        }
    )
    bot, created = Bot.objects.get_or_create(
        user=user,
        defaults={
            'personality': personality
        }
    )

    return user

def create_post(bot):
    content = generate_post(bot.bot.personality)

    Post.objects.create(author=bot, content=content)

def like_post(bot, post):
        post.likes.add(bot)

def reply_to_post(bot, post):
    content = generate_reply(bot.bot.personality, post.content)

    Post.objects.create(author=bot, content=content, parent=post)

def run_bots():
    bots = User.objects.filter(is_bot=True)

    bots_to_create = 20 - len(bots)

    if bots_to_create > 0:
        for i in range(bots_to_create):
            create_bot(BOT_DESCRIPTIONS[i][0], BOT_DESCRIPTIONS[i][1])

        bots = User.objects.filter(is_bot=True)

    for bot in bots:
        posts = get_recommended_posts(bot)

        if random.random() < 0.05: create_post(bot)

        for post in posts:
            alignment = get_post_alignment(post.content, bot.bot.personality)

            if (alignment['scores'][0] > 0.5):
                if alignment['scores'][0] + random.random() > 1.3: like_post(bot, post)
                if alignment['scores'][0] + random.random() > 1.5: reply_to_post(bot, post)

            if (alignment['scores'][1] > 0.5):
                if alignment['scores'][1] + random.random() > 1.8: reply_to_post(bot, post)

class Command(BaseCommand):
    help = 'Run bot scheduler'

    def handle(self, *args, **kwargs):
        run_bots()
        schedule.every(15).minutes.do(run_bots)
        self.stdout.write(self.style.SUCCESS('Bot scheduler started...'))

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Bot scheduler stopped by user (Ctrl+C)'))