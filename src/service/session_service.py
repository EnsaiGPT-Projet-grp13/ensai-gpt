from __future__ import annotations
from typing import Any, Dict, Optional
from objects.session import Session


class SessionService:
    """Wrap léger autour de Session pour centraliser les accès."""

    def __init__(self) -> None:
        self._s = Session()

    def get_user_id(self) -> int:
        return int(self._s.utilisateur.get("id_utilisateur"))

    def set_personnage(self, pid: int, name: str, system_prompt: str) -> None:
        self._s.personnage = {
            "id_personnageIA": pid,
            "name": name,
            "system_prompt": system_prompt,
        }

    def get_personnage(self) -> Optional[Dict[str, Any]]:
        return getattr(self._s, "personnage", None)

    def set_conversation_info(
        self,
        cid: int,
        titre: str,
        is_collab: bool,
        token: Optional[str],
    ) -> None:
        self._s.conversation_id = cid
        self._s.conversation_title = titre
        self._s.conversation_is_collab = is_collab
        self._s.conversation_token = token

    def get_conversation_id(self) -> Optional[int]:
        return getattr(self._s, "conversation_id", None)

    def set_conversation_title(self, titre: str) -> None:
        self._s.conversation_title = titre

    def get_conversation_title(self) -> Optional[str]:
        return getattr(self._s, "conversation_title", None)
