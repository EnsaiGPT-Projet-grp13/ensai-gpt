# src/service/conversation_service.py
import os
import requests
from typing import Dict, Any, List, Optional, Tuple

from src.objects.conversation import Conversation
from src.objects.message import Message
from src.dao.conversation_dao import ConversationDao
from src.dao.message_dao import MessageDao

API_URL = os.getenv("API_URL", "https://ensai-gpt-109912438483.europe-west4.run.app/generate")


class ConversationService:
    def __init__(self):
        self.conv_dao = ConversationDao()
        self.msg_dao = MessageDao()

    # ---------- création / reprise ----------
    def start(
        self,
        id_user: int,
        personnage: Dict[str, Any],
        titre: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Conversation:
        conv = Conversation(
            id_conversation=None,
            id_proprio=id_user,
            id_personnageIA=personnage["id_personnageIA"],
            titre=titre,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return self.conv_dao.create(conv)

    def get(self, cid: int) -> Optional[Conversation]:
        return self.conv_dao.find_by_id(cid)

    def list_for_user(self, uid: int, limit: int = 25):
        return self.conv_dao.list_by_user(uid, limit=limit)

    # ---------- historique ----------
    def build_history(self, personnage: Dict[str, Any], cid: int) -> List[Dict[str, str]]:
        history: List[Dict[str, str]] = [{"role": "system", "content": personnage["system_prompt"]}]
        for m in self.msg_dao.list_for_conversation(cid):
            role = "assistant" if m.expediteur == "IA" else "user"
            history.append({"role": role, "content": m.contenu})
        return history

    # ---------- extraction texte IA ----------
    def _extract_ai_text(self, resp: requests.Response) -> str:
        try:
            data = resp.json()
        except Exception:
            return (resp.text or "").strip() or "[IA] Réponse vide."

        if isinstance(data, dict):
            for key in ("content", "text", "reply"):
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()

            msg = data.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    msg = first.get("message")
                    if isinstance(msg, dict):
                        content = msg.get("content")
                        if isinstance(content, str) and content.strip():
                            return content.strip()
                    for key in ("text", "content", "reply"):
                        val = first.get(key)
                        if isinstance(val, str) and val.strip():
                            return val.strip()

        return (str(data) or "").strip() or "[IA] Réponse vide."

    # ---------- cycle complet : save user -> call API -> save IA ----------
    def send_user_and_get_ai(
        self,
        cid: int,
        id_user: int,
        personnage: Dict[str, Any],
        user_text: str,
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 150,
    ) -> Tuple[str, Dict[str, Any]]:
        # 1) message utilisateur
        self.msg_dao.add(Message(
            id_message=None,
            id_conversation=cid,
            expediteur="utilisateur",
            id_utilisateur=id_user,
            contenu=user_text,
        ))

        # 2) historique complet
        history = self.build_history(personnage, cid)
        payload = {
            "history": history,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }

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
        self.conv_dao.touch(cid)

        return ia_text, payload
