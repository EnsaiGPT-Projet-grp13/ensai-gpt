import os
from typing import List
from psycopg2.extras import RealDictCursor
from src.dao.db import DBConnection
from src.objects.message import Message

SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")

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

    def recherche_mots_message(self, id_utilisateur: int, mots: str, limite: int = 5) -> List[Dict[str, Any]]:
        """Recherche une suite de caractères dans les messages d'un utilisateur et renvoie les messages associés"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  m.id_message,
                  m.id_conversation,
                  m.expediteur,
                  m.contenu,
                  m.id_utilisateur,
                  m.create_at
                FROM {SCHEMA}.message m
                WHERE m.id_utilisateur = %s
                ORDER BY create_at DESC
                LIMIT %s
                """,
                (id_utilisateur, limite),
            )
            return cur.fetchall() or []
