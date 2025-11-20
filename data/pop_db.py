import os
import sys

from dao.db import DBConnection
from service.utilisateur_service import UtilisateurService
from utils.securite import hash_password
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_DIR)



USERS = [
    ("John", "Beau", "john.beau@gmail.com", "JohnBeau5", "2000-01-01"),
    ("Alice", "Martin", "alice.martin@example.com", "Alice123", "1998-05-20"),
    ("Paul", "Durand", "paul.durand@example.com", "Paulo42", "1997-07-15"),
    ("Sophie", "Bernard", "sophie.bernard@example.com", "Soso99", "2001-09-30"),
    ("Luc", "Petit", "luc.petit@example.com", "Luc!2024", "1999-12-25"),
    ("Emma", "Dubois", "emma.dubois@example.com", "EmmaPwd7", "2002-03-11"),
    ("Max", "Roux", "max.roux@example.com", "MaxRoux8", "1996-04-18"),
    ("Nina", "Lefevre", "nina.lefevre@example.com", "Nina1234", "2003-07-12"),
]


def main():
    conn = DBConnection().connection
    service = UtilisateurService()
    inserted_users = 0

    with conn.cursor() as cur:
        cur.execute("SET search_path TO projetGPT;")
        for prenom, nom, mail, mdp, naiss in USERS:
            mail_norm = mail.strip().lower()
            mdp_hache = hash_password(mdp, mail_norm)
            cur.execute(
                """
                INSERT INTO utilisateur (prenom, nom, mail, mdp, naiss)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (mail) DO NOTHING
                RETURNING id_utilisateur;
                """,
                (prenom, nom, mail_norm, mdp_hache, naiss),
            )
            res = cur.fetchone()
            if res:
                uid = res[0] if isinstance(res, tuple) else res.get("id_utilisateur")
                service.add_default_persoIA(uid)
                inserted_users += 1

    conn.commit()
    print(f"{inserted_users}/{len(USERS)} utilisateurs insérés.")


if __name__ == "__main__":
    main()
