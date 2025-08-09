# from django.test import TransactionTestCase
# import google.generativeai as genai

# API_KEY = 'AIzaSyBYZReEMC8bh8n_B0K5O3iT4cg-PlO_Zww'
# genai.configure(api_key=API_KEY)

# model = genai.GenerativeModel('gemini-1.5-flash')

# prompt = 'Jeśteś użytkownikiem portalu Xter podobnego do Twittera. Twoja osobowość: Jesteś fanem sportu i Janusza Korwin-Mikke. Napisz post maksymalnie kilkuzdaniowy, który jest zgodny z Twoją osobowością.'

# response = model.generate_content(prompt)

# print(response.text)

from transformers import pipeline

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

print(get_post_alignment('Korwin-mikke jest chujowy', 'Jesteś fanem sportu i Janusza Korwin-Mikke.'))