# src/service/message_service.py
from __future__ import annotations
from src.dao.message_dao import MessageDao
#from utils. import api call_ensai_gpt

class ChatService:
    """
    Gère l'historique local du chat (en mémoire) et l'appel à l'IA.
    Plus tard, tu pourras brancher ici tes DAO pour persister sessions/messages.
    """

    def __init__(self, system_prompt: str = "Tu es un assistant utile.") -> None:
        self.history: list[dict] = [{"role": "system", "content": system_prompt}]
        self.message_dao = MessageDao()

    def ask(self, user_content: str) -> str:
        """Ajoute le message utilisateur, appelle l'IA, enregistre la réponse et la renvoie."""
        self.history.append({"role": "user", "content": user_content})
        answer = call_ensai_gpt(self.history)
        self.history.append({"role": "assistant", "content": answer})
        return answer

    def recherche_mots_message(self, id_utilisateur: int, mots: str, limite: int = 5):
        """Renvoie la liste des messages dans lesquels mots est présent"""
        return self.message_dao.recherche_mots_message(id_utilisateur, mots, limite=limite)

    def affichage_message_conversartion(self, id_conversation: int):
        """Renvoie toutes la suite des messages d'une conversation"""
        liste_message = MessageDao().list_for_conversation(id_conversation)
        if not liste_message:
            print("Aucun message trouvé pour cette conversation.")
            return
        for message in liste_message:
            print("\n" + f"Message de {message.expediteur :}" + "-" *50 + "\n")
            print(f"{message.contenu}")

        
