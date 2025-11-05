# conversation_service.py
from __future__ import annotations

import os
import requests
import secrets
import string
from typing import Dict, Any, List, Optional, Tuple

from objects.conversation import Conversation
from objects.message import Message
from dao.conversation_dao import ConversationDao
from dao.message_dao import MessageDao


API_URL = os.getenv("API_URL", "https://ensai-gpt-109912438483.europe-west4.run.app/generate")


def _gen_token(n: int = 16) -> str:
    """Génère un token alphanumérique (A-Z, 0-9) de longueur n."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


class ConversationService:
    """
    Service applicatif : gère la création et la persistance des conversations,
    la construction de l'historique, l'appel à l'API et l'enregistrement des messages.
    Aucune logique d'interface (pas d'InquirerPy ici).
    """

    def __init__(self) -> None:
        self.conv_dao = ConversationDao()
        self.msg_dao = MessageDao()

    # --------------------------------------------------------------------- #
    # CRUD / accès conversations
    # --------------------------------------------------------------------- #
    def start(
        self,
        id_user: int,
        personnage: Dict[str, Any],
        titre: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        is_collab: bool = False,
        token_override: Optional[str] = None,
    ) -> Conversation:
        # ⚠️ Normaliser les valeurs avant de créer l’objet
        if max_tokens is None:
            max_tokens = 150  # aligne-toi sur le DEFAULT DB
        # (optionnel) caster pour éviter surprises
        if temperature is not None:
            temperature = float(temperature)
        if top_p is not None:
            top_p = float(top_p)

        token = token_override or (_gen_token(16) if is_collab else None)

        conv = Conversation(
            id_conversation=None,
            id_proprio=id_user,
            id_personnageIA=personnage["id_personnageIA"],
            titre=titre,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,   # ✅ jamais None
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

    def liste_proprietaire_pour_utilisateur(self, id_utilisateur: int, limite: int = 25):
        """Liste des conversations dont l'utilisateur est propriétaire."""
        return self.conv_dao.liste_proprietaire_pour_utilisateur(id_utilisateur, limite=limite)

    def liste_accessible_pour_utilisateur(self, id_utilisateur: int, limite: int = 50):
        """Liste des conversations accessibles."""
        return self.conv_dao.liste_accessible_pour_utilisateur(id_utilisateur, limite=limite)

    def liste_resumee_proprietaire_pour_utilisateur(self, id_utilisateur: int, limite: int = 25):
        """Liste résumée (titre + nom personnage) des conversations dont l'utilisateur est propriétaire."""
        return self.conv_dao.liste_resumee_proprietaire_pour_utilisateur(id_utilisateur, limite=limite)

    def liste_resumee_accessible_pour_utilisateur(self, id_utilisateur: int, limite: int = 50):
        """Liste résumée (titre + nom personnage) des conversations auxquelles l'utilisateur a accès."""
        return self.conv_dao.liste_resumee_accessible_pour_utilisateur(id_utilisateur, limite=limite)

    def recherche_mots_titre(self, id_utilisateur: int, mots: str, limite: int = 50):
        """Renvoie la liste des conversations dans lesquelles mots est présent dans le titre"""
        return self.conv_dao.recherche_mots_titre(id_utilisateur, mots, limite=limite)

    # --------------------------------------------------------------------- #
    # Construction payload API
    # --------------------------------------------------------------------- #
    def build_history(self, personnage: Dict[str, Any], cid: int) -> List[Dict[str, str]]:
        """
        Construit l'historique complet au format attendu par l'API :
        [{role:'system'|'user'|'assistant', content:'...'}, ...]
        """
        history: List[Dict[str, str]] = [
            {"role": "system", "content": personnage["system_prompt"]}
        ]
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
        JSON conforme à l'OAS de ton endpoint:
        {
          "history": [...],
          "temperature": ...,
          "top_p": ...,
          "max_tokens": ...,
          "stop": [...]
        }
        """
        payload: Dict[str, Any] = {
            "history": self.build_history(personnage, cid),
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_tokens": int(max_tokens),
        }
        if stop:
            payload["stop"] = stop
        return payload

    # --------------------------------------------------------------------- #
    # Appel API + extraction robuste du texte
    # --------------------------------------------------------------------- #
    @staticmethod
    def _extract_ai_text(resp: requests.Response) -> str:
        """
        Gestion de formats de réponse variés (string brute ou style OpenAI-like).
        Retourne toujours une string non vide.
        """
        try:
            data = resp.json()
        except Exception:
            return (resp.text or "").strip() or "[IA] Réponse vide."

        if isinstance(data, str):
            return data.strip() or "[IA] Réponse vide."

        if isinstance(data, dict):
            # Format OpenAI-like
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0] if isinstance(choices[0], dict) else None
                if isinstance(first, dict):
                    msg = first.get("message")
                    if isinstance(msg, dict):
                        content = msg.get("content")
                        if isinstance(content, str) and content.strip():
                            return content.strip()
                    for key in ("text", "content", "reply"):
                        v = first.get(key)
                        if isinstance(v, str) and v.strip():
                            return v.strip()

            msg = data.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

            for key in ("content", "text", "reply"):
                v = data.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()

            detail = data.get("detail")
            if isinstance(detail, list) and detail:
                msgs = [d.get("msg") for d in detail if isinstance(d, dict) and d.get("msg")]
                if msgs:
                    return "[API] " + " | ".join(msgs)

            return (str(data) or "").strip() or "[IA] Réponse vide."

        return (str(data) or "").strip() or "[IA] Réponse vide."

    # --------------------------------------------------------------------- #
    # Cycle complet : save user -> call API -> save IA
    # --------------------------------------------------------------------- #
    def send_user_and_get_ai(
        self,
        cid: int,
        id_user: int,
        personnage: Dict[str, Any],
        user_text: str,
        *,
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

        # 2) payload
        payload = self._make_payload(
            personnage, cid, temperature, top_p, max_tokens, stop=stop
        )

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
