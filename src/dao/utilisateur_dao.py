from typing import Optional
from objects.utilisateur import Utilisateur
from dao.db import DBConnection

class UtilisateurDao:
    
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

        """Trouver un utilisateur par son ID."""
        with DBConnection().connection as conn:  # Connexion à la base de données
            with conn.cursor() as cur:  # Curseur pour exécuter la requête
                cur.execute("""
                    SELECT id_utilisateur, prenom, nom, mail, mdp AS mdp_hash, naiss
                    FROM utilisateur
                    WHERE id_utilisateur = %s
                """, (id_utilisateur,))
                row = cur.fetchone()
                
        # Si un utilisateur est trouvé, on retourne un objet Utilisateur
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

    def update_nom_utilisateur(self, utilisateur: Utilisateur) -> bool:
        """Met à jour un utilisateur dans la base de données."""
        conn = DBConnection().connection
        with conn.cursor() as cur:
            # Préparer la requête SQL pour mettre à jour les informations de l'utilisateur
            cur.execute("""
                UPDATE utilisateur
                SET prenom = %s, nom = %s, mail = %s, mdp = %s, naiss = %s
                WHERE id_utilisateur = %s
            """, (utilisateur.prenom, utilisateur.nom_utilisateur, utilisateur.mail, utilisateur.mdp_hash, utilisateur.naiss, utilisateur.id_utilisateur))

            # Commit des changements sans vérifier si des lignes ont été affectées
            conn.commit()
            return True  # Retourne toujours True, peu importe si la mise à jour a eu lieu ou non
            
    def update_mail_utilisateur(self, utilisateur: Utilisateur) -> bool:
        """Met à jour un utilisateur dans la base de données."""
        conn = DBConnection().connection
        with conn.cursor() as cur:
            # Préparer la requête SQL pour mettre à jour les informations de l'utilisateur
            cur.execute("""
                UPDATE utilisateur
                SET prenom = %s, nom = %s, mail = %s, mdp = %s, naiss = %s
                WHERE mail= %s
            """, (utilisateur.prenom, utilisateur.nom_utilisateur, utilisateur.mail, utilisateur.mdp_hash, utilisateur.naiss, utilisateur.id_utilisateur))

            # Commit des changements sans vérifier si des lignes ont été affectées
            conn.commit()
            return True  # Retourne toujours True, peu importe si la mise à jour a eu lieu ou non

    def delete(self, id_utilisateur: int) -> None:
        """Supprime un utilisateur de la base de données."""
        conn = DBConnection.get_conn() if hasattr(DBConnection, "get_conn") else DBConnection().connection
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM utilisateur
                WHERE id_utilisateur = %s
            """, (id_utilisateur,))
        conn.commit()
