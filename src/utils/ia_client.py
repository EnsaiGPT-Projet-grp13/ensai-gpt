# src/utils/ia_client.py
import os
import requests

class IAClient:
    """Client pour appeler l'API ENSAI-GPT"""

    def __init__(self, system_prompt: str = "Tu es un assistant utile."):
        host = os.getenv(
            "WEBSERVICE_HOST",
            "https://ensai-gpt-109912438483.europe-west4.run.app",
        ).rstrip("/")
        self.api_url = f"{host}/generate"

        self.system_prompt = system_prompt
        self.history = [{"role": "system", "content": self.system_prompt}]

        # hyperparamètres
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.top_p = float(os.getenv("LLM_TOP_P", "1.0"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "300"))

    def ask(self, user_msg: str) -> str:
        """Ajoute un message utilisateur et envoie l’historique à l’API"""
        self.history.append({"role": "user", "content": user_msg})

        payload = {
            "history": self.history,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }

        try:
            r = requests.post(self.api_url, json=payload, timeout=30)
            r.raise_for_status()
        except Exception as e:
            return f"[Erreur réseau/API] {e}"

        try:
            data = r.json()
        except Exception:
            return f"[Erreur parsing JSON] Réponse brute: {r.text}"

        # formats possibles
        if isinstance(data, str):
            answer = data
        elif isinstance(data, dict) and "content" in data:
            answer = data["content"]
        else:
            answer = str(data)

        # on enrichit l’historique
        self.history.append({"role": "assistant", "content": answer})
        return answer
