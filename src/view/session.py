# src/view/session.py
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
        # Pour éviter les erreurs .get(...) partout, on préfère un dict vide plutôt que None
        self.utilisateur: Dict[str, Any] = {}
        self.personnage: Optional[Dict[str, Any]] = None
        self.debut_connexion: Optional[str] = None
        # Champ libre si tu veux attacher un id_session DB plus tard
        self.session: Any = None

    # ---------- Gestion utilisateur ----------
    def connexion(self, utilisateur: Dict[str, Any]) -> None:
        """
        Enregistre l'utilisateur en session.
        Attendu: {id_utilisateur, prenom, nom, mail, ...}
        """
        self.utilisateur = dict(utilisateur or {})
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def deconnexion(self) -> None:
        """Purge complète de la session."""
        self.utilisateur = {}
        self.personnage = None
        self.debut_connexion = None
        self.session = None

    # ---------- Gestion personnage ----------
    def set_personnage(self, personnage: Dict[str, Any]) -> None:
        """
        Définit le personnage actif.
        Attendu: {id_personnageIA, name, system_prompt}
        """
        if not personnage or "id_personnageIA" not in personnage:
            raise ValueError("Personnage invalide")
        self.personnage = dict(personnage)

    def clear_personnage(self) -> None:
        """Efface le personnage actif."""
        self.personnage = None

    # ---------- Affichage ----------
    def afficher(self) -> str:
        """Retourne un récapitulatif lisible de la session."""
        u = self.utilisateur or {}
        p = self.personnage or {}

        lignes = [
            "Actuellement en session :",
            "-------------------------",
            f"debut_connexion : {self.debut_connexion}",
            f"utilisateur.id : {u.get('id_utilisateur', '(non connecté)')}",
            f"utilisateur    : {u.get('prenom','')} {u.get('nom','')} <{u.get('mail','')}>",
            f"personnage     : {p.get('name', '(aucun)')}",
        ]
        return "\n".join(lignes)
