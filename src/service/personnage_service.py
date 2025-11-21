from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from dao.personnage_ia_dao import PersonnageIADao
from objects.personnage_ia import PersonnageIA
from utils.log_decorator import log

try:
    import dotenv

    dotenv.load_dotenv(override=True)
except Exception:
    pass

LLM_MAX_TOKENS = os.getenv("LLM_MAX_TOKENS", 300)


class PersonnageService:
    """Service métier pour la gestion des personnages IA (aucune logique d’UI)."""

    def __init__(self) -> None:
        self.dao = PersonnageIADao()

    def lister_personnages_ia_crees_par(self, uid: int) -> List[PersonnageIA]:
        """Retourne les personnages créés par un utilisateur spécifique."""
        return self.dao.lister_personnages_ia_crees_par(uid)

    def get_by_id(self, pid: int) -> Optional[PersonnageIA]:
        """Récupère un personnage par son ID."""
        return self.dao.find_by_id(pid)

    def create_personnage(
        self, uid: int, name: str, system_prompt: str
    ) -> PersonnageIA:
        """
        Crée un personnage IA avec created_by = uid.
        """
        perso = PersonnageIA(
            id_personnageIA=None,
            name=name.strip(),
            system_prompt=system_prompt.strip(),
            created_by=uid,
        )
        return self.dao.create(perso)

    @log
    def supprimer_personnage_ia(self, user_id: int, personnage_id: int) -> bool:
        """
        Supprime un personnage IA appartenant à l'utilisateur, ainsi que
        ses conversations et messages.
        Retourne True si la suppression a réussi, False sinon.
        """
        persos = self.dao.lister_personnages_ia_crees_par(user_id)
        if not any(p.id_personnageIA == personnage_id for p in persos):
            return False

        return self.dao.delete(personnage_id)

    @log
    def lister_personnages_ia_pour_utilisateur(
        self, user_id: int
    ) -> list[PersonnageIA]:
        """
        Retourne les personnages IA d'un utilisateur
        """
        return self.dao.lister_personnages_ia_pour_utilisateur(user_id)
