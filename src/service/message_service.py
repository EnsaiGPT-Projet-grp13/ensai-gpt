# src/service/message_service.py
from __future__ import annotations
from src.dao.message_dao import MessageDao
#from utils. import api call_ensai_gpt

class MessageService:
    """
    Gère l'historique local du chat (en mémoire) et l'appel à l'IA.
    Plus tard, tu pourras brancher ici tes DAO pour persister sessions/messages.
    """

    def __init__(self, system_prompt: str = "Tu es un assistant utile.") -> None:
        self.history: list[dict] = [{"role": "system", "content": system_prompt}]
        self.message_dao = MessageDao()



    def recherche_mots_message(self, id_utilisateur: int, mots: str, limite: int = 5):
        """Renvoie la liste des messages dans lesquels mots est présent"""
        return self.message_dao.recherche_mots_message(id_utilisateur, mots, limite=limite)
        
