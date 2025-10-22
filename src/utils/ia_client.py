import os
import requests

class IAClient:
    def __init__(self, system_prompt: str):
        self.api_url = os.getenv(
            "WEBSERVICE_HOST",
            "https://ensai-gpt-109912438483.europe-west4.run.app",
        ).rstrip("/") + "/generate"
        self.history = [{"role": "system", "content": system_prompt}]

    def ask(self, user_msg: str) -> str:
        self.history.append({"role": "user", "content": user_msg})
        payload = {
            "history": self.history,
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "top_p": float(os.getenv("LLM_TOP_P", "1.0")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "300")),
        }

        r = requests.post(self.api_url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()

        # Extraire uniquement le texte de la réponse
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            content = str(data)

        self.history.append({"role": "assistant", "content": content})
        return content
