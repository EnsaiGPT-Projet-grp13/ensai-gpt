# dao/personnage_ia_dao.py
import os
from typing import Optional, List
from psycopg2.extras import RealDictCursor
from dao.db import DBConnection
from objects.personnage_ia import PersonnageIA

SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")


class PersonnageIADao:
    """DAO personnageIA + gestion du lien persoIA_utilisateur."""

    def __init__(self) -> None:
        self.conn = DBConnection().connection

    # --- Lien user <-> perso ------------------------------------------------
    def add(self, id_utilisateur: int, id_personnageIA: int) -> None:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.persoIA_utilisateur (id_utilisateur, id_personnageIA)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (id_utilisateur, id_personnageIA),
            )
        self.conn.commit()

    def remove(self, id_utilisateur: int, id_personnageIA: int) -> None:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                DELETE FROM {SCHEMA}.persoIA_utilisateur
                WHERE id_utilisateur = %s AND id_personnageIA = %s
                """,
                (id_utilisateur, id_personnageIA),
            )
        self.conn.commit()

    def list_personnage_ids_for_user(self, uid: int) -> List[int]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id_personnageIA
                FROM {SCHEMA}.persoIA_utilisateur
                WHERE id_utilisateur = %s
                """,
                (uid,),
            )
            rows = cur.fetchall() or []
        return [r["id_personnageIA"] for r in rows]

    # --- CRUD personnageIA ---------------------------------------------------
    def create(self, p: PersonnageIA) -> PersonnageIA:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.personnageIA (name, system_prompt, created_by)
                VALUES (%s, %s, %s)
                RETURNING
                  id_personnageIA AS "id_personnageIA",
                  name,
                  system_prompt,
                  created_by,
                  created_at,
                  updated_at
                """,
                (p.name, p.system_prompt, p.created_by),
            )
            row = cur.fetchone()
        self.conn.commit()
        return PersonnageIA(**row)

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

    def update(self, p: PersonnageIA) -> Optional[PersonnageIA]:
        if p.id_personnageIA is None:
            return None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                UPDATE {SCHEMA}.personnageIA
                SET name = %s,
                    system_prompt = %s
                WHERE id_personnageIA = %s
                RETURNING
                  id_personnageIA AS "id_personnageIA",
                  name,
                  system_prompt,
                  created_by,
                  created_at,
                  updated_at
                """,
                (p.name, p.system_prompt, p.id_personnageIA),
            )
            row = cur.fetchone()
        self.conn.commit()
        return PersonnageIA(**row) if row else None

    def delete(self, pid: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {SCHEMA}.personnageIA WHERE id_personnageIA = %s",
                (pid,),
            )
            affected = cur.rowcount
        self.conn.commit()
        return affected > 0

    # --- Listes --------------------------------------------------------------
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
                ORDER BY lower(name)
                """
            )
            rows = cur.fetchall() or []
        return [PersonnageIA(**r) for r in rows]

    def list_by_creator(self, uid: int) -> List[PersonnageIA]:
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
                WHERE created_by = %s
                ORDER BY lower(name)
                """,
                (uid,),
            )
            rows = cur.fetchall() or []
        return [PersonnageIA(**r) for r in rows]

    def list_for_user(self, uid: int) -> List[PersonnageIA]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT * FROM (
                    SELECT
                        p.id_personnageIA AS "id_personnageIA",
                        p.name,
                        p.system_prompt,
                        p.created_by,
                        p.created_at,
                        p.updated_at
                    FROM {SCHEMA}.personnageIA p
                    WHERE p.created_by IS NULL

                    UNION ALL

                    SELECT
                        p.id_personnageIA AS "id_personnageIA",
                        p.name,
                        p.system_prompt,
                        p.created_by,
                        p.created_at,
                        p.updated_at
                    FROM {SCHEMA}.personnageIA p
                    JOIN {SCHEMA}.persoIA_utilisateur pu
                        ON pu.id_personnageIA = p.id_personnageIA
                    WHERE pu.id_utilisateur = %s

                    UNION ALL

                    SELECT
                        p.id_personnageIA AS "id_personnageIA",
                        p.name,
                        p.system_prompt,
                        p.created_by,
                        p.created_at,
                        p.updated_at
                    FROM {SCHEMA}.personnageIA p
                    WHERE p.created_by = %s
                ) AS all_persos
                ORDER BY lower(all_persos.name)
                """,
                (uid, uid),
            )
            rows = cur.fetchall() or []
        return [PersonnageIA(**r) for r in rows]
