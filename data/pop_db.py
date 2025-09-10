import sys
import os

# Permet d'importer src/ depuis data/
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.dao.db_connection import DBConnection
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
        cur.execute("SET search_path TO projetGPT;")  # ⚠️ tu peux remplacer par os.getenv("POSTGRES_SCHEMA")
        for prenom, nom, mail, pwd, naiss in USERS:
            hashed = hash_pwd(pwd)
            cur.execute(
                """
                INSERT INTO utilisateur (prenom, nom, mail, mdp, naiss)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (mail) DO NOTHING;
                """,
                (prenom, nom, mail, hashed, naiss),
            )
        conn.commit()
    print(f"{len(USERS)} utilisateurs insérés.")

if __name__ == "__main__":
    main()
