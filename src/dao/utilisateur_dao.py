from typing import Optional
from objects.utilisateur import Utilisateur
from dao.db import DBConnection

class UtilisateurDao:

    def update(self, u: Utilisateur) -> bool:
        """Met à jour mail et mdp_hash (et éventuellement prénom/nom)."""
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE utilisateur
            SET prenom = %s,
                nom = %s,
                mail = %s,
                mdp_hash = %s,
                naiss = %s
            WHERE id_utilisateur = %s
            """,
            (u.prenom, u.nom, u.mail, u.mdp_hash, u.naiss, u.id_utilisateur),
        )
        self.conn.commit()
        return cur.rowcount == 1
    
    def find_by_mail(self, mail: str) -> Optional[Utilisateur]:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_utilisateur, prenom, nom, mail, mdp AS mdp_hash, naiss
                FROM utilisateur
                WHERE mail = %s
            """, (mail,))
            row = cur.fetchone()
        return Utilisateur(**row) if row else None
    
    def find_by_id(self, id_utilisateur: int) -> Optional[Utilisateur]:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_utilisateur, prenom, nom, mail, mdp AS mdp_hash, naiss
                FROM utilisateur
                WHERE id_utilisateur = %s
            """, (id_utilisateur,))
            row = cur.fetchone()
        return Utilisateur(**row) if row else None


    def exists_mail(self, mail: str) -> bool:
        conn = DBConnection.get_conn() if hasattr(DBConnection, "get_conn") else DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_utilisateur, prenom, nom, mail, mdp AS mdp_hash, naiss
                FROM utilisateur
                WHERE id_utilisateur = %s
            """, (id_utilisateur,))
            row = cur.fetchone()
        return Utilisateur(**row) if row else None

    def exists_mail(self, mail: str) -> bool:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM utilisateur WHERE mail = %s", (mail,))
            return cur.fetchone() is not None

    def create(self, u: Utilisateur) -> Utilisateur:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO utilisateur (prenom, nom, mail, mdp, naiss)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_utilisateur
            """, (u.prenom, u.nom, u.mail, u.mdp_hash, u.naiss))
            u.id_utilisateur = cur.fetchone()["id_utilisateur"]
        conn.commit()
        return u

    def update_mot_de_passe(self, id_utilisateur: int, nouveau_hash: str) -> None:
        """Met à jour le mot de passe d'un utilisateur."""
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE utilisateur
                SET mdp = %s
                WHERE id_utilisateur = %s
            """, (nouveau_hash, id_utilisateur))
        conn.commit()
        
    def update_identite(self, utilisateur: Utilisateur) -> bool:
        """
        Met à jour le prénom et le nom d'un utilisateur.
        Retourne True si exactement une ligne a été modifiée.
        """
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE utilisateur
                SET prenom = %s,
                    nom    = %s
                WHERE id_utilisateur = %s
                """,
                (utilisateur.prenom, utilisateur.nom, utilisateur.id_utilisateur),
            )
            affected = cur.rowcount
            conn.commit()
            return affected == 1

    def update_mail_utilisateur(self, utilisateur: Utilisateur) -> bool:
        """
        Met à jour l'adresse mail d'un utilisateur.
        Retourne True si exactement une ligne a été modifiée.
        """
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE utilisateur
                SET mail = %s
                WHERE id_utilisateur = %s
                """,
                (utilisateur.mail, utilisateur.id_utilisateur),
            )
            affected = cur.rowcount
            conn.commit()
            return affected == 1

    def delete(self, id_utilisateur: int) -> None:
        """Supprime un utilisateur de la base de données."""
        conn = DBConnection.get_conn() if hasattr(DBConnection, "get_conn") else DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM utilisateur
                WHERE id_utilisateur = %s
            """, (id_utilisateur,))
        conn.commit()
