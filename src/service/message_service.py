# src/service/message_service.py
from __future__ import annotations
from utils. import api call_ensai_gpt

class ChatService:
    """
    Gère l'historique local du chat (en mémoire) et l'appel à l'IA.
    Plus tard, tu pourras brancher ici tes DAO pour persister sessions/messages.
    """

    def __init__(self, system_prompt: str = "Tu es un assistant utile.") -> None:
        self.history: list[dict] = [{"role": "system", "content": system_prompt}]

    def ask(self, user_content: str) -> str:
        """Ajoute le message utilisateur, appelle l'IA, enregistre la réponse et la renvoie."""
        self.history.append({"role": "user", "content": user_content})
        answer = call_ensai_gpt(self.history)
        self.history.append({"role": "assistant", "content": answer})
        return answer
