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

    def list_by_user(self, uid: int, limit: int = 25) -> List[Conversation]:
        """Conversations DONT l’utilisateur est propriétaire (pour compat historique simple)."""
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

    def list_accessible_by_user(self, uid: int, limit: int = 50) -> List[Conversation]:
        """Conversations accessibles = propriétaire OU membre conv_utilisateur."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  c.id_conversation AS "id_conversation",
                  c.id_proprio,
                  c.id_personnageIA AS "id_personnageIA",
                  c.titre,
                  c.created_at,
                  c.updated_at,
                  c.temperature,
                  c.top_p,
                  c.max_tokens,
                  c.is_collab,
                  c.token_collab
                FROM {SCHEMA}.conversation c
                WHERE c.id_proprio = %s
                UNION
                SELECT
                  c.id_conversation AS "id_conversation",
                  c.id_proprio,
                  c.id_personnageIA AS "id_personnageIA",
                  c.titre,
                  c.created_at,
                  c.updated_at,
                  c.temperature,
                  c.top_p,
                  c.max_tokens,
                  c.is_collab,
                  c.token_collab
                FROM {SCHEMA}.conversation c
                JOIN {SCHEMA}.conv_utilisateur cu ON cu.id_conversation = c.id_conversation
                WHERE cu.id_utilisateur = %s
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (uid, uid, limit),
            )
            rows = cur.fetchall() or []
        return [Conversation(**r) for r in rows]

    def list_summaries_by_user(self, uid: int, limit: int = 25) -> List[Dict[str, Any]]:
        """Résumé propriétaire uniquement (titre + nom perso)."""
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
                ORDER BY c.updated_at DESC
                LIMIT %s
                """,
                (uid, limit),
            )
            return cur.fetchall() or []

    def list_summaries_accessible(self, uid: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Résumé propriétaire + membres (sans ID conv)."""
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
                (uid, uid, limit),
            )
            return cur.fetchall() or []

    def touch(self, cid: int) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                f'UPDATE {SCHEMA}.conversation SET titre = titre WHERE id_conversation = %s',
                (cid,),
            )
        self.conn.commit()
