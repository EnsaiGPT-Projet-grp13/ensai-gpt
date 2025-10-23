from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

from utils.singleton import Singleton

class Session(metaclass=Singleton):
    """
    Session applicative (Singleton).
    - utilisateur : dict avec au minimum {id_utilisateur, prenom, nom, mail}
    - personnage  : dict avec {id_personnageIA, name, system_prompt} ou None
    - debut_connexion : str "dd/mm/YYYY HH:MM:SS"
    """
    def __init__(self) -> None:
        self.utilisateur: Dict[str, Any] = {}
        self.personnage: Optional[Dict[str, Any]] = None
        self.debut_connexion: Optional[str] = None
        self.session: Any = None
        self.conversation_id: Optional[int] = None
        self.conversation_title: Optional[str] = None

    def connexion(self, utilisateur: Dict[str, Any]) -> None:
        self.utilisateur = dict(utilisateur or {})
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def deconnexion(self) -> None:
        self.utilisateur = {}
        self.personnage = None
        self.debut_connexion = None
        self.session = None
        self.conversation_id = None
        self.conversation_title = None

    def set_personnage(self, personnage: Dict[str, Any]) -> None:
        if not personnage or "id_personnageIA" not in personnage:
            raise ValueError("Personnage invalide")
        self.personnage = dict(personnage)

    def clear_personnage(self) -> None:
        self.personnage = None

    def afficher(self) -> str:
        u = self.utilisateur or {}
        p = self.personnage or {}
        return (
            "Actuellement en session :\n"
            "-------------------------\n"
            f"debut_connexion : {self.debut_connexion}\n"
            f"utilisateur.id : {u.get('id_utilisateur','(non connecté)')}\n"
            f"utilisateur    : {u.get('prenom','')} {u.get('nom','')} <{u.get('mail','')}>\n"
            f"personnage     : {p.get('name','(aucun)')}\n"
            f"conversation_id: {self.conversation_id}\n"
        )
