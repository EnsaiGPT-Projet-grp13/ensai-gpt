import os
from typing import Optional, List
from psycopg2.extras import RealDictCursor
from dao.db import DBConnection
from objects.personnage_ia import PersonnageIA

SCHEMA = os.getenv("POSTGRES_SCHEMA", "projetGPT")

class PersonnageIADao:
    """DAO pour la table personnageIA (sans table d'association)."""

    def __init__(self) -> None:
        self.conn = DBConnection().connection

    # --- CRUD personnageIA ---------------------------------------------------
    def create(self, p: PersonnageIA) -> PersonnageIA:
        """
        UPSERT sur (name, created_by) :
        - insert si nouveau
        - update system_prompt si déjà existant
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO {SCHEMA}.personnageIA (name, system_prompt, created_by)
                VALUES (%s, %s, %s)
                ON CONFLICT (name, created_by) DO UPDATE
                    SET system_prompt = EXCLUDED.system_prompt,
                        updated_at = NOW()
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
            if row is None:
                raise Exception("Erreur lors de l'insertion ou mise à jour de l'objet.")
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
        """
        Supprime un personnage IA et tout ce qui est lié :
          - messages des conversations du personnage
          - liens conv_utilisateur
          - conversations du personnage
          - le personnage lui-même
        """
        try:
            with self.conn.cursor() as cur:
                # 1) Supprimer les messages des conversations liées à ce personnage
                cur.execute(
                    f"""
                    DELETE FROM {SCHEMA}.message
                    WHERE id_conversation IN (
                        SELECT id_conversation
                        FROM {SCHEMA}.conversation
                        WHERE id_personnageIA = %s
                    )
                    """,
                    (pid,),
                )

                # 2) Supprimer les liens conv_utilisateur pour ces conversations
                cur.execute(
                    f"""
                    DELETE FROM {SCHEMA}.conv_utilisateur
                    WHERE id_conversation IN (
                        SELECT id_conversation
                        FROM {SCHEMA}.conversation
                        WHERE id_personnageIA = %s
                    )
                    """,
                    (pid,),
                )

                # 3) Supprimer les conversations de ce personnage
                cur.execute(
                    f"""
                    DELETE FROM {SCHEMA}.conversation
                    WHERE id_personnageIA = %s
                    """,
                    (pid,),
                )

                # 4) Supprimer le personnage lui-même
                cur.execute(
                    f"""
                    DELETE FROM {SCHEMA}.personnageIA
                    WHERE id_personnageIA = %s
                    """,
                    (pid,),
                )
                affected = cur.rowcount

            self.conn.commit()
            return affected > 0

        except Exception:
            self.conn.rollback()
            raise


        

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
        """Retourne les personnages standards + ceux créés par l'utilisateur."""
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
