from __future__ import annotations

import os
import requests
import secrets
import string
from typing import Dict, Any, List, Optional, Tuple

from src.objects.conversation import Conversation
from src.objects.message import Message
from src.dao.conversation_dao import ConversationDao
from src.dao.message_dao import MessageDao

# URL de ton endpoint (via .env si présent)
API_URL = os.getenv("API_URL", "https://ensai-gpt-109912438483.europe-west4.run.app/generate")


def _gen_token(n: int = 16) -> str:
    """Token alphanumérique (A-Z, 0-9) de longueur n pour token_collab."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


class ConversationService:
    """Service applicatif pour gérer conversation + messages + appel à l'API IA."""

    def __init__(self) -> None:
        self.conv_dao = ConversationDao()
        self.msg_dao = MessageDao()

    # -------------------------------------------------------------------------
    # Création / accès
    # -------------------------------------------------------------------------
    def start(
        self,
        id_user: int,
        personnage: Dict[str, Any],
        titre: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        is_collab: bool = False,
    ) -> Conversation:
        """Crée une conversation (privée ou collaborative) et la retourne."""
        token = _gen_token(16) if is_collab else None
        conv = Conversation(
            id_conversation=None,
            id_proprio=id_user,
            id_personnageIA=personnage["id_personnageIA"],
            titre=titre,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            is_collab=is_collab,
            token_collab=token,
        )
        return self.conv_dao.create(conv)

    def join_by_token(self, id_user: int, token: str) -> Optional[Conversation]:
        """Rejoint une conversation collaborative via token (et ajoute l'utilisateur aux participants)."""
        token = (token or "").strip().upper()
        if not token:
            return None
        conv = self.conv_dao.find_by_token(token)
        if not conv:
            return None
        self.conv_dao.add_participant(id_user, conv.id_conversation)
        return conv

    def get(self, cid: int) -> Optional[Conversation]:
        return self.conv_dao.find_by_id(cid)

    def list_for_user(self, uid: int, limit: int = 25):
        """Conversations dont l'utilisateur est **propriétaire**."""
        return self.conv_dao.list_by_user(uid, limit=limit)

    def list_accessible_for_user(self, uid: int, limit: int = 50):
        """Conversations **accessibles** (proprio + celles rejointes)."""
        return self.conv_dao.list_accessible_by_user(uid, limit=limit)

    def list_summaries_for_user(self, uid: int, limit: int = 25):
        """Résumés propriétaire uniquement (titre + nom personnage)."""
        return self.conv_dao.list_summaries_by_user(uid, limit=limit)

    def list_summaries_accessible_for_user(self, uid: int, limit: int = 50):
        """Résumés accessibles (titre + nom personnage)."""
        return self.conv_dao.list_summaries_accessible(uid, limit=limit)

    # -------------------------------------------------------------------------
    # Historique / payload
    # -------------------------------------------------------------------------
    def build_history(self, personnage: Dict[str, Any], cid: int) -> List[Dict[str, str]]:
        """
        Construit l'historique complet au format attendu par l'API :
        [{role:'system'|'user'|'assistant', content:'...'}, ...]
        """
        history: List[Dict[str, str]] = [{"role": "system", "content": personnage["system_prompt"]}]
        for m in self.msg_dao.list_for_conversation(cid):
            role = "assistant" if m.expediteur == "IA" else "user"
            history.append({"role": role, "content": m.contenu})
        return history

    def _make_payload(
        self,
        personnage: Dict[str, Any],
        cid: int,
        temperature: float,
        top_p: float,
        max_tokens: int,
        stop: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Construit le JSON strictement conforme à ton OAS :
        {
          "history": [...],
          "temperature": ...,
          "top_p": ...,
          "max_tokens": ...,
          "stop": [...]
        }
        """
        payload = {
            "history": self.build_history(personnage, cid),
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        if stop:
            payload["stop"] = stop
        return payload

    # -------------------------------------------------------------------------
    # Appel IA : extraction robuste du texte
    # -------------------------------------------------------------------------
    def _extract_ai_text(self, resp: requests.Response) -> str:
        """
        L'OAS indique que la réponse 200 est une **string JSON**.
        Mais certains backends renvoient parfois un objet façon OpenAI :
        {"choices":[{"message":{"content":"..."}}], ...}
        On gère les deux et on garantit une string non vide.
        """
        try:
            data = resp.json()
        except Exception:
            return (resp.text or "").strip() or "[IA] Réponse vide."

        # 1) Format conforme à l'OAS : la réponse EST une chaîne
        if isinstance(data, str):
            return data.strip() or "[IA] Réponse vide."

        # 2) Formats tolérés (OpenAI/Mistral proxy)
        if isinstance(data, dict):
            # choices[0].message.content
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0] if isinstance(choices[0], dict) else None
                if isinstance(first, dict):
                    msg = first.get("message")
                    if isinstance(msg, dict):
                        content = msg.get("content")
                        if isinstance(content, str) and content.strip():
                            return content.strip()
                    # parfois le texte est directement dans choice
                    for key in ("text", "content", "reply"):
                        v = first.get(key)
                        if isinstance(v, str) and v.strip():
                            return v.strip()
            # message.content à la racine
            msg = data.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
            # clés simples à la racine
            for key in ("content", "text", "reply"):
                v = data.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()

            # Erreur de validation FastAPI ?
            detail = data.get("detail")
            if isinstance(detail, list) and detail:
                msgs = []
                for d in detail:
                    if isinstance(d, dict) and isinstance(d.get("msg"), str):
                        msgs.append(d["msg"])
                if msgs:
                    return "[API] " + " | ".join(msgs)

            return (str(data) or "").strip() or "[IA] Réponse vide."

        # 3) autre type JSON
        return (str(data) or "").strip() or "[IA] Réponse vide."

    # -------------------------------------------------------------------------
    # Cycle complet : save user -> call API -> save IA
    # -------------------------------------------------------------------------
    def send_user_and_get_ai(
        self,
        cid: int,
        id_user: int,
        personnage: Dict[str, Any],
        user_text: str,
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 150,
        stop: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        1) Sauvegarde le message utilisateur
        2) Construit le payload et appelle l'API
        3) Sauvegarde la réponse IA
        4) Met à jour updated_at de la conversation
        5) Retourne (texte_IA, payload_envoyé)
        """
        # 1) message utilisateur
        self.msg_dao.add(Message(
            id_message=None,
            id_conversation=cid,
            expediteur="utilisateur",
            id_utilisateur=id_user,
            contenu=user_text,
        ))

        # 2) payload conforme
        payload = self._make_payload(personnage, cid, temperature, top_p, max_tokens, stop=stop)

        # (optionnel) debug :
        # if os.getenv("DEBUG_PAYLOAD", "0") == "1":
        #     import json
        #     dbg = dict(payload)
        #     if len(dbg.get("history", [])) > 3:
        #         dbg["history"] = dbg["history"][:2] + [{"role": "...", "content": "...(tronqué)..."}, dbg["history"][-1]]
        #     print(json.dumps(dbg, ensure_ascii=False, indent=2))

        # 3) appel API
        try:
            resp = requests.post(API_URL, json=payload, timeout=60)
            if resp.status_code != 200:
                ia_text = f"[API {resp.status_code}] {resp.text}"
            else:
                ia_text = self._extract_ai_text(resp)
        except Exception as e:
            ia_text = f"[API] Exception: {repr(e)}"

        if not isinstance(ia_text, str) or not ia_text.strip():
            ia_text = "[IA] Réponse vide."

        # 4) message IA
        self.msg_dao.add(Message(
            id_message=None,
            id_conversation=cid,
            expediteur="IA",
            id_utilisateur=None,
            contenu=ia_text,
        ))
        # 5) MAJ updated_at
        self.conv_dao.touch(cid)

        return ia_text, payload
