from google import genai
from google.genai import types

client = genai.Client()

system_instructions = '''
    Jesteś użytkownikiem portalu Xter podobnego do X/Twittera.
    Twoja nazwa użytkownika: hamara
    Twoja nazwa: hamara
    Twoja osobowość: Jesteś neutralnym użytkownikiem.
    Napisz jedno-, dwu- lub trzyzdaniową odpowiedź, która jest zgodna z Twoją osobowością. Wygeneruj jedynie treść bez żadnych dodatkowych informacji.
'''

# Historia w formacie lista dict (SDK akceptuje to bezpośrednio)
history = [
    {"role": "user", "parts": ["Hej, co sądzisz o nowej funkcji Xter?"]},
    {"role": "model", "parts": ["Myślę, że jest całkiem przydatna dla użytkowników."]},
    {"role": "user", "parts": ["Czy będzie działać na wszystkich urządzeniach?"]}
]

chat = client.chats.create(
    model='gemini-2.5-flash-lite',  # Twój model działa
    config=types.GenerateContentConfig(
        system_instruction=system_instructions  # uproszczona forma z docsów
    ),
    history=history  # teraz SDK wspiera parametr history w chats.create
)

post = 'Tak, wszystkie platformy powinny być wspierane.'

response = chat.send_message(post)
print(response.text)