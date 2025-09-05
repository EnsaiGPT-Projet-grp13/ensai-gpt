import os
import requests

API_URL = "https://ensai-gpt-109912438483.europe-west4.run.app/generate"

payload = {
    "history": [
        {"role": "system", "content": "Tu es un assistant utile."},
        {"role": "user", "content": "Bonjour, peux-tu me donner une citation inspirante ?"}
    ],
    "temperature": 0.7,
    "top_p": 1.0,
    "max_tokens": 150
}

response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    print("Réponse de l'IA :", response.json())
else:
    print("Erreur :", response.status_code, response.text)
