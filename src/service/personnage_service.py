# service/personnage_service.py
from __future__ import annotations
from typing import Dict, Any, List, Optional

from objects.personnage_ia import PersonnageIA
from dao.personnage_ia_dao import PersonnageIADao


class PersonnageService:
    """Service métier pour la gestion des personnages IA (aucune logique d’UI)."""

    def __init__(self) -> None:
        self.dao = PersonnageIADao()

    # ---------------------------------------------------------
    # Lecture / Récupération
    # ---------------------------------------------------------
    def list_for_user(self, uid: int) -> List[PersonnageIA]:
        """
        Retourne tous les personnages visibles par l'utilisateur :
        - standards (créés par le système)
        - liés via persoIA_utilisateur
        - créés par cet utilisateur.
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
    # Création / Lien utilisateur
    # ---------------------------------------------------------
    def create_personnage(self, uid: int, name: str, system_prompt: str) -> PersonnageIA:
        """
        Crée un personnage IA (created_by = uid),
        puis ajoute un lien vers l'utilisateur pour qu'il le voie immédiatement.
        """
        perso = PersonnageIA(
            id_personnageIA=None,
            name=name.strip(),
            system_prompt=system_prompt.strip(),
            created_by=uid,
        )

        # Insertion en base
        perso = self.dao.create(perso)

        # Lier le personnage à l'utilisateur (table persoIA_utilisateur)
        self.dao.add(uid, perso.id_personnageIA)
        return perso

    def link_to_user(self, uid: int, pid: int) -> None:
        """Lie un personnage existant à un utilisateur."""
        self.dao.add(uid, pid)

    def unlink_from_user(self, uid: int, pid: int) -> None:
        """Supprime le lien entre un utilisateur et un personnage."""
        self.dao.remove(uid, pid)

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
        """Supprime un personnage de la base (et ses liens si cascade configurée)."""
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
        max_tokens: int = 150,
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
