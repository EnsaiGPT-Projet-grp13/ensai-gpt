import os
from typing import Optional, List
from psycopg2.extras import RealDictCursor
from src.dao.db import DBConnection
from src.objects.conversation import Conversation

SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")

class ConversationDao:
    def __init__(self):
        self.conn = DBConnection().connection

    def create(self, conv: Conversation) -> Conversation:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.conversation
                    (id_proprio, id_personnageIA, titre, temperature, top_p, max_tokens, is_collab, token_collab)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                  id_conversation AS "id_conversation",
                  id_proprio,
                  id_personnageIA AS "id_personnageIA",
                  titre,
                  created_at,
                  updated_at,
                  temperature,
                  top_p,
                  max_tokens,
                  is_collab,
                  token_collab
                """,
                (
                    conv.id_proprio, conv.id_personnageIA, conv.titre,
                    conv.temperature, conv.top_p, conv.max_tokens,
                    conv.is_collab, conv.token_collab
                ),
            )
            row = cur.fetchone()
        self.conn.commit()
        # On reconstruit l'objet avec les clés alignées sur la dataclass
        return Conversation(**row)

    def find_by_id(self, cid: int) -> Optional[Conversation]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  id_conversation AS "id_conversation",
                  id_proprio,
                  id_personnageIA AS "id_personnageIA",
                  titre,
                  created_at,
                  updated_at,
                  temperature,
                  top_p,
                  max_tokens,
                  is_collab,
                  token_collab
                FROM {SCHEMA}.conversation
                WHERE id_conversation = %s
                """,
                (cid,),
            )
            row = cur.fetchone()
        return Conversation(**row) if row else None

    def list_by_user(self, uid: int, limit: int = 25) -> List[Conversation]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  id_conversation AS "id_conversation",
                  id_proprio,
                  id_personnageIA AS "id_personnageIA",
                  titre,
                  created_at,
                  updated_at,
                  temperature,
                  top_p,
                  max_tokens,
                  is_collab,
                  token_collab
                FROM {SCHEMA}.conversation
                WHERE id_proprio = %s
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (uid, limit),
            )
            rows = cur.fetchall() or []
        return [Conversation(**r) for r in rows]
