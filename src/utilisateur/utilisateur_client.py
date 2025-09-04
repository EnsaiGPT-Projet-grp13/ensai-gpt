import os
import requests
from typing import List, Dict


class UtilisateurClient:
    """Make calls to the IA endpoint for chat interactions"""

    def __init__(self) -> None:
        # Récupère l’URL de l’API 
        self.__host = os.environ["WEBSERVICE_HOST"]

    # fonction pour créer une nouvelle session de chat (associer un utilisateur à une conversation)
    def start_chat_session(self, user_id: int) -> str:
        pass

    # fonction pour envoyer un message de l’utilisateur à l’IA
    def send_message(self, session_id: str, message: str) -> str:
        pass

    # fonction pour récupérer l’historique des messages d’une session
    def get_chat_history(self, session_id: str) -> List[Dict]:
        pass

    # fonction pour terminer une session (optionnel)
    def end_chat_session(self, session_id: str) -> bool:
        pass
