# src/view/session.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

from utils.singleton import Singleton

class Session(metaclass=Singleton):
    def __init__(self) -> None:
        self.utilisateur = {}
        self.personnage = None
        self.debut_connexion = None
        self.session = None
        self.conversation_id = None          # <--- AJOUT

    def deconnexion(self) -> None:
        self.utilisateur = {}
        self.personnage = None
        self.debut_connexion = None
        self.session = None
        self.conversation_id = None          # <--- AJOUT

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
