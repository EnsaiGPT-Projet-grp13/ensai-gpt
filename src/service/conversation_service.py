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

    # --- déjà présent ---
    def start(self, id_user: int, personnage: Dict[str, Any], titre: Optional[str]=None,
              temperature: Optional[float]=None, top_p: Optional[float]=None, max_tokens: Optional[int]=None) -> Conversation:
        conv = Conversation(
            id_conversation=None,
            id_proprio=id_user,
            id_personnageIA=personnage["id_personnageIA"],
            titre=titre,
            temperature=temperature, top_p=top_p, max_tokens=max_tokens,
        )
        return self.conv_dao.create(conv)

    def list_for_user(self, uid: int, limit: int = 25):
        return self.conv_dao.list_by_user(uid, limit=limit)

    def build_history(self, personnage: Dict[str, Any], cid: int) -> List[Dict[str, str]]:
        # L’API exige l’historique complet (y compris system)
        history: List[Dict[str, str]] = [{"role": "system", "content": personnage["system_prompt"]}]
        for m in self.msg_dao.list_for_conversation(cid):
            role = "assistant" if m.expediteur == "IA" else "user"
            history.append({"role": role, "content": m.contenu})
        return history


    def _make_payload(self, personnage: Dict[str, Any], cid: int,
                      temperature: float, top_p: float, max_tokens: int,
                      stop: Optional[List[str]] = None) -> Dict[str, Any]:
        payload = {
            "history": self.build_history(personnage, cid),
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        if stop:
            payload["stop"] = stop
        return payload


    def _extract_ai_text(self, resp) -> str:
        """
        Ton API *devrait* renvoyer une string JSON (ex: "Bonjour !").
        Si jamais un proxy renvoie un objet façon OpenAI/Mistral, on récupère
        choices[0].message.content. Toujours retourner une str non vide.
        """
        try:
            data = resp.json()
        except Exception:
            # Pas de JSON -> texte brut
            return (resp.text or "").strip() or "[IA] Réponse vide."

        # --- Format conforme à l'OAS: JSON = string ---
        if isinstance(data, str):
            return data.strip() or "[IA] Réponse vide."

        # --- Formats tolérés (proxy OpenAI/Mistral) ---
        if isinstance(data, dict):
            # 1) choices[0].message.content
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

            # 2) message.content au niveau racine
            msg = data.get("message")
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

            # 3) clés simples au niveau racine
            for key in ("content", "text", "reply"):
                v = data.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()

            # 4) Erreur de validation FastAPI (422) -> agréger les messages
            detail = data.get("detail")
            if isinstance(detail, list) and detail:
                msgs = []
                for d in detail:
                    if isinstance(d, dict) and isinstance(d.get("msg"), str):
                        msgs.append(d["msg"])
                if msgs:
                    return "[API] " + " | ".join(msgs)

            # Fallback: stringifier l'objet
            return (str(data) or "").strip() or "[IA] Réponse vide."

        # JSON d'un autre type (liste, etc.)
        return (str(data) or "").strip() or "[IA] Réponse vide."



    def send_user_and_get_ai(
        self, cid: int, id_user: int, personnage: Dict[str, Any], user_text: str,
        temperature: float = 0.7, top_p: float = 1.0, max_tokens: int = 150,
        stop: Optional[List[str]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        # 1) sauver le message utilisateur
        self.msg_dao.add(Message(
            id_message=None,
            id_conversation=cid,
            expediteur="utilisateur",
            id_utilisateur=id_user,
            contenu=user_text,
        ))

        # 2) payload strict conforme
        payload = self._make_payload(personnage, cid, temperature, top_p, max_tokens, stop=stop)

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

        # 4) sauver la réponse IA
        self.msg_dao.add(Message(
            id_message=None,
            id_conversation=cid,
            expediteur="IA",
            id_utilisateur=None,
            contenu=ia_text,
        ))
        # mettre à jour updated_at
        self.conv_dao.touch(cid)

        return ia_text, payload
