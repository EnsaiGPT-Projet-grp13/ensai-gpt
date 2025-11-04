import os
from typing import Optional, List, Dict, Any
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

    def find_by_token(self, token: str) -> Optional[Conversation]:
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
                WHERE token_collab = %s AND is_collab = TRUE
                """,
                (token,),
            )
            row = cur.fetchone()
        return Conversation(**row) if row else None

    def add_participant(self, uid: int, cid: int) -> None:
        """Donne accès à un utilisateur à une conversation (table d'association)."""
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.conv_utilisateur (id_utilisateur, id_conversation)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (uid, cid),
            )
        self.conn.commit()

    def list_by_user(self, id_utilisateur: int, limite: int = 25) -> List[Conversation]:
        """Renvoie les conversations dont l’utilisateur est propriétaire."""
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
                (id_utilisateur, limite),
            )
            rows = cur.fetchall() or []
        return [Conversation(**r) for r in rows]

    def list_accessible_by_user(self, id_utilisateur: int, limite: int = 50) -> List[Conversation]:
        """Renvoie les conversations accessibles, à la fois propriétaire ou simple membre."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  *
                FROM {SCHEMA}.conversation c
                WHERE c.id_proprio = %s
                UNION
                SELECT
                  *
                FROM {SCHEMA}.conversation c
                JOIN {SCHEMA}.conv_utilisateur cu ON cu.id_conversation = c.id_conversation
                WHERE cu.id_utilisateur = %s
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (id_utilisateur, id_utilisateur, limite),
            )
            rows = cur.fetchall() or []
        return [Conversation(**r) for r in rows]

    def list_summaries_by_user(self, id_utilisateur: int, limite: int = 25) -> List[Dict[str, Any]]:
        """Renvoie un résumé des conversations (titre + nom personnageIA) dont l’utilisateur est propriétaire."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  c.titre,
                  p.name AS "personnageIA_name"
                FROM {SCHEMA}.conversation c
                JOIN {SCHEMA}.personnageIA p ON p.id_personnageIA = c.id_personnageIA
                WHERE c.id_proprio = %s
                ORDER BY c.updated_at DESC
                LIMIT %s
                """,
                (id_utilisateur, limite),
            )
            return cur.fetchall() or []

    def list_summaries_accessible(self, id_utilisateur: int, limite: int = 50) -> List[Dict[str, Any]]:
        """Renvoie un résumé des conversations (titre + nom personnageIA) dont l’utilisateur a l'accès."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  c.titre,
                  p.name AS "personnage_name",
                  c.created_at,
                  c.updated_at
                FROM {SCHEMA}.conversation c
                JOIN {SCHEMA}.personnageIA p ON p.id_personnageIA = c.id_personnageIA
                WHERE c.id_proprio = %s
                UNION
                SELECT
                  c.titre,
                  p.name AS "personnage_name",
                  c.created_at,
                  c.updated_at
                FROM {SCHEMA}.conversation c
                JOIN {SCHEMA}.personnageIA p ON p.id_personnageIA = c.id_personnageIA
                JOIN {SCHEMA}.conv_utilisateur cu ON cu.id_conversation = c.id_conversation
                WHERE cu.id_utilisateur = %s
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (id_utilisateur, id_utilisateur, limite),
            )
            return cur.fetchall() or []

    def touch(self, cid: int) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                f'UPDATE {SCHEMA}.conversation SET titre = titre WHERE id_conversation = %s',
                (cid,),
            )
        self.conn.commit()
