# src/dao/session_dao.py
import os
from typing import Optional, List, Dict, Any
from psycopg2.extras import RealDictCursor
from dao.db import DBConnection

SCHEMA = os.getenv("POSTGRES_SCHEMA", "projetGPT")

class SessionDao:
    """
    DAO pour gérer les sessions utilisateurs :
    - ouverture d'une session
    - fermeture d'une session
    - récupération des sessions actives / historiques
    """

    def __init__(self):
        self.conn = DBConnection().connection

    def open(self, id_utilisateur: int) -> Optional[int]:
        """Crée une nouvelle session en BDD et retourne son id."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.session (id_utilisateur)
                VALUES (%s)
                RETURNING id_session;
                """,
                (id_utilisateur,)
            )
            row = cur.fetchone()
        self.conn.commit()
        return row["id_session"] if row else None

    def close(self, id_session: int) -> bool:
        """Marque la session comme terminée (ended_at = NOW())."""
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE {SCHEMA}.session
                SET ended_at = NOW()
                WHERE id_session = %s AND ended_at IS NULL;
                """,
                (id_session,)
            )
            updated = cur.rowcount
        self.conn.commit()
        return updated > 0

    def find_active_by_user(self, id_utilisateur: int) -> Optional[Dict[str, Any]]:
        """Retourne la session active du user (ended_at IS NULL)."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id_session, id_utilisateur, started_at, ended_at
                FROM {SCHEMA}.session
                WHERE id_utilisateur = %s
                AND ended_at IS NULL
                ORDER BY started_at DESC
                LIMIT 1;
                """,
                (id_utilisateur,)
            )
            return cur.fetchone()

    def list_by_user(self, id_utilisateur: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Liste les sessions (anciennes et actives) d’un utilisateur."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id_session, id_utilisateur, started_at, ended_at
                FROM {SCHEMA}.session
                WHERE id_utilisateur = %s
                ORDER BY started_at DESC
                LIMIT %s;
                """,
                (id_utilisateur, limit)
            )
            return cur.fetchall() or []
