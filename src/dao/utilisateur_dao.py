from typing import Optional
from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection

class UtilisateurDao:
    def find_by_mail(self, mail: str) -> Optional[Utilisateur]:
        conn = DBConnection.get_conn() if hasattr(DBConnection, "get_conn") else DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_utilisateur, prenom, nom, mail, mdp AS mdp_hash, naiss
                FROM utilisateur
                WHERE mail = %s
            """, (mail,))
            row = cur.fetchone()
        return Utilisateur(**row) if row else None

    def exists_mail(self, mail: str) -> bool:
        conn = DBConnection.get_conn() if hasattr(DBConnection, "get_conn") else DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM utilisateur WHERE mail = %s", (mail,))
            return cur.fetchone() is not None

    def create(self, u: Utilisateur) -> Utilisateur:
        conn = DBConnection.get_conn() if hasattr(DBConnection, "get_conn") else DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO utilisateur (prenom, nom, mail, mdp, naiss)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_utilisateur
            """, (u.prenom, u.nom, u.mail, u.mdp_hash, u.naiss))
            u.id_utilisateur = cur.fetchone()["id_utilisateur"]
        conn.commit()
        return u
