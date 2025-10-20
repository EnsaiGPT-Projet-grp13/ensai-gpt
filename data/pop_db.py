import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.dao.db import DBConnection
from src.utils.securite import hash_pwd

USERS = [
    ("John", "Beau", "john.beau@gmail.com", "JohnBeau5", "2000-01-01"),
    ("Alice", "Martin", "alice.martin@example.com", "Alice123", "1998-05-20"),
    ("Paul", "Durand", "paul.durand@example.com", "Paulo42", "1997-07-15"),
    ("Sophie", "Bernard", "sophie.bernard@example.com", "Soso99", "2001-09-30"),
    ("Luc", "Petit", "luc.petit@example.com", "Luc!2024", "1999-12-25"),
    ("Emma", "Dubois", "emma.dubois@example.com", "EmmaPwd7", "2002-03-11"),
]

def main():
    conn = DBConnection().connection
    with conn.cursor() as cur:
        cur.execute("SET search_path TO projetgpt;") 
        for prenom, nom, mail, mdp, naiss in USERS:
            mdp_hache = hash_pwd(mdp, mail)
            cur.execute(
                """
                INSERT INTO utilisateur (prenom, nom, mail, mdp, naiss)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (mail) DO NOTHING;
                """,
                (prenom, nom, mail, mdp_hache, naiss),
            )
        conn.commit()
    print(f"{len(USERS)} utilisateurs ont été insérés dans la database utilisateur.")

    

if __name__ == "__main__":
    main()
