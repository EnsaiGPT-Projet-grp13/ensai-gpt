# src/view/session.py
from utils.singleton import Singleton
from typing import Optional, Dict, Any
from datetime import datetime

class Session(metaclass=Singleton):
    def __init__(self) -> None:
        self.utilisateur: Dict[str, Any] = {}
        self.personnage: Optional[Dict[str, Any]] = None
        self.debut_connexion: Optional[str] = None
        self.session: Any = None
        self.conversation_id: Optional[int] = None
        self.conversation_title: Optional[str] = None
        self.conversation_is_collab: bool = False
        self.conversation_token: Optional[str] = None

    def deconnexion(self) -> None:
        self.utilisateur = {}
        self.personnage = None
        self.debut_connexion = None
        self.session = None
        self.conversation_id = None
        self.conversation_title = None
        self.conversation_is_collab = False
        self.conversation_token = None
