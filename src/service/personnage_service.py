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

    # ---------------------------------------------------------
    # Lecture / Récupération
    # ---------------------------------------------------------
    def list_for_user(self, uid: int) -> List[PersonnageIA]:
        """
        Retourne les personnages visibles par l'utilisateur :
        - standards (créés par le système)
        - créés par cet utilisateur (created_by = uid)
        """
        return self.dao.list_for_user(uid)

    def list_standards(self) -> List[PersonnageIA]:
        """Retourne les personnages standards (créés par le système)."""
        return self.dao.list_standards()

    def list_by_creator(self, uid: int) -> List[PersonnageIA]:
        """Retourne les personnages créés par un utilisateur spécifique."""
        return self.dao.list_by_creator(uid)

    def get_by_id(self, pid: int) -> Optional[PersonnageIA]:
        """Récupère un personnage par son ID."""
        return self.dao.find_by_id(pid)

    # ---------------------------------------------------------
    # Création
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Mise à jour / Suppression
    # ---------------------------------------------------------
    def update_personnage(
        self,
        pid: int,
        *,
        name: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Optional[PersonnageIA]:
        """
        Met à jour le nom et/ou le prompt système du personnage.
        Retourne le personnage mis à jour, ou None si l'ID n'existe pas.
        """
        current = self.dao.find_by_id(pid)
        if not current:
            return None

        if isinstance(name, str) and name.strip():
            current.name = name.strip()
        if isinstance(system_prompt, str) and system_prompt.strip():
            current.system_prompt = system_prompt.strip()

        return self.dao.update(current)

    def delete_personnage(self, pid: int) -> bool:
        """Supprime un personnage de la base."""
        return self.dao.delete(pid)

    # ---------------------------------------------------------
    # Utilitaire pour l’API d’IA
    # ---------------------------------------------------------
    @staticmethod
    def build_payload(
        personnage: PersonnageIA | Dict[str, Any],
        user_messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = LLM_MAX_TOKENS,
    ) -> Dict[str, Any]:
        """
        Construit l’historique complet pour l’appel à l’API IA.
        Le premier message est toujours le 'system_prompt' du personnage.
        """
        sp = (
            personnage.system_prompt
            if isinstance(personnage, PersonnageIA)
            else personnage["system_prompt"]
        )

        history = [{"role": "system", "content": sp}]
        history.extend(user_messages)

        return {
            "history": history,
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_tokens": int(max_tokens),
        }

    @log
    def lister_personnages_ia_crees_par(self, user_id: int) -> list[PersonnageIA]:
        """
        Retourne la liste des personnages IA créés par un utilisateur.
        (wrapping de PersonnageIADao.list_by_creator)
        """
        return self.dao.list_by_creator(user_id)

    @log
    def supprimer_personnage_ia(self, user_id: int, personnage_id: int) -> bool:
        """
        Supprime un personnage IA appartenant à l'utilisateur, ainsi que
        ses conversations et messages (via PersonnageIADao.delete).
        Retourne True si la suppression a réussi, False sinon.
        """
        # Vérifier que ce personnage appartient bien à cet utilisateur
        persos = self.dao.list_by_creator(user_id)
        if not any(p.id_personnageIA == personnage_id for p in persos):
            # Le personnage n'est pas à lui → on ne supprime pas
            return False

        # Appel à la méthode delete du DAO qui supprime aussi les conversations/messages
        return self.dao.delete(personnage_id)

    @log
    def lister_personnages_ia_pour_utilisateur(
        self, user_id: int
    ) -> list[PersonnageIA]:
        """
        Retourne les personnages IA disponibles pour un utilisateur :
        - personnages standards
        - + personnages créés par l'utilisateur
        (wrapping de PersonnageIADao.list_for_user)
        """
        return self.dao.list_for_user(user_id)
