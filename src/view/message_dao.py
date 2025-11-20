import os
from typing import List, Dict, Any
from psycopg2.extras import RealDictCursor
from dao.db import DBConnection
from objects.message import Message

SCHEMA = os.getenv("POSTGRES_SCHEMA", "projetGPT")

class MessageDao:
    def __init__(self):
        self.conn = DBConnection().connection


    def add(self, msg: Message) -> Message:
        contenu = (msg.contenu or "").strip()
        if not contenu:
            contenu = "[vide]"
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.message
                    (id_conversation, expediteur, id_utilisateur, contenu)
                VALUES (%s, %s, %s, %s)
                RETURNING id_message AS "id_message", created_at
                """,
                (msg.id_conversation, msg.expediteur, msg.id_utilisateur, contenu),
            )
            row = cur.fetchone()
            msg.id_message = row["id_message"]
            msg.created_at = row["created_at"]
        self.conn.commit()
        return msg


    def list_for_conversation(self, cid: int) -> List[Message]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  id_message AS "id_message",
                  id_conversation, expediteur, id_utilisateur, contenu, created_at
                FROM {SCHEMA}.message
                WHERE id_conversation = %s
                ORDER BY created_at ASC, id_message ASC
                """,
                (cid,),
            )
            rows = cur.fetchall() or []
        return [Message(**r) for r in rows]

    def get_title(self, cid: int) -> str:
        """Retourne le titre d'une conversation, ou '(sans titre)' si introuvable."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT titre
                FROM {SCHEMA}.conversation
                WHERE id_conversation = %s
                """,
                (cid,),
            )
            row = cur.fetchone()

        if not row:
            return "(sans titre)"

        titre = (row["titre"] or "").strip()
        return titre if titre else "(sans titre)"
