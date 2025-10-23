import os
from typing import Optional, List
from psycopg2.extras import RealDictCursor
from src.dao.db import DBConnection
from src.objects.personnage_ia import PersonnageIA

SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")

class PersonnageIADao:
    def __init__(self):
        self.conn = DBConnection().connection

    def create(self, p: PersonnageIA) -> PersonnageIA:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.personnageIA (name, system_prompt, created_by)
                VALUES (%s, %s, %s)
                RETURNING id_personnageIA AS "id_personnageIA"
                """,
                (p.name, p.system_prompt, p.created_by),
            )
            p.id_personnageIA = cur.fetchone()["id_personnageIA"]
        self.conn.commit()
        return p

    def find_by_id(self, pid: int) -> Optional[PersonnageIA]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  id_personnageIA AS "id_personnageIA",
                  name,
                  system_prompt,
                  created_by,
                  created_at,
                  updated_at
                FROM {SCHEMA}.personnageIA
                WHERE id_personnageIA = %s
                """,
                (pid,),
            )
            row = cur.fetchone()
        return PersonnageIA(**row) if row else None

    def list_standards(self) -> List[PersonnageIA]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  id_personnageIA AS "id_personnageIA",
                  name,
                  system_prompt,
                  created_by,
                  created_at,
                  updated_at
                FROM {SCHEMA}.personnageIA
                WHERE created_by IS NULL
                ORDER BY name
                """
            )
            rows = cur.fetchall() or []
        return [PersonnageIA(**r) for r in rows]

    def list_for_user(self, uid: int) -> List[PersonnageIA]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                  id_personnageIA AS "id_personnageIA",
                  name,
                  system_prompt,
                  created_by,
                  created_at,
                  updated_at
                FROM {SCHEMA}.personnageIA
                WHERE created_by IS NULL
                UNION ALL
                SELECT
                  id_personnageIA AS "id_personnageIA",
                  name,
                  system_prompt,
                  created_by,
                  created_at,
                  updated_at
                FROM {SCHEMA}.personnageIA
                WHERE created_by = %s
                ORDER BY name
                """,
                (uid,),
            )
            rows = cur.fetchall() or []
        return [PersonnageIA(**r) for r in rows]
