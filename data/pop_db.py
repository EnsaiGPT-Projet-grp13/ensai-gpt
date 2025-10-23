# data/pop_db.py
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dao.db import DBConnection
from src.utils.securite import hash_pwd

USERS = [
    ("John", "Beau",   "john.beau@gmail.com",            "JohnBeau5", "2000-01-01"),
    ("Alice","Martin", "alice.martin@example.com",       "Alice123",  "1998-05-20"),
    ("Paul", "Durand", "paul.durand@example.com",        "Paulo42",   "1997-07-15"),
    ("Sophie","Bernard","sophie.bernard@example.com",    "Soso99",    "2001-09-30"),
    ("Luc",  "Petit",  "luc.petit@example.com",          "Luc!2024",  "1999-12-25"),
    ("Emma", "Dubois", "emma.dubois@example.com",        "EmmaPwd7",  "2002-03-11"),
]

PERSONNAGES = [
    ("Jardinier",
     "Tu es Jardinier, expert en potager et entretien durable. "
     "Donne des conseils concrets et saisonniers (France), étapes courtes, outils simples, sécurité et écologie. "
     "Propose des alternatives sans pesticides et des calendriers de semis/récolte.",
     None),
    ("Boulanger",
     "Tu es Boulanger artisanal. Explique les recettes de pains et viennoiseries avec grammages en g, "
     "températures et temps de pousse. Donne des astuces de pétrissage, façonnage, cuisson et conservation.",
     None),
    ("Prof de maths",
     "Tu es Prof de maths pédagogue (lycée/licence). Donne définitions, théorèmes, exemples et contre-exemples. "
     "Explique étape par étape, corrige les erreurs fréquentes, puis propose un exercice d'application court.",
     None),
    ("Médecin généraliste",
     "Tu es Médecin généraliste. Tu donnes des informations générales et de la prévention. "
     "Tu ne poses pas de diagnostic. Encourage à consulter en cas de symptômes sérieux ou persistants.",
     None),
    ("Développeur Python",
     "Tu es Développeur Python senior. Réponds avec du code clair, idiomatique, testé rapidement. "
     "Précise la complexité quand pertinent et propose des alternatives (stdlib vs packages).",
     None),
    ("Coach sportif",
     "Tu es Coach sportif. Programmes simples, progressifs et sûrs. "
     "Adapte aux niveaux, précise échauffement, technique, récupération et fréquence.",
     None),
    ("Conseiller voyage",
     "Tu es Conseiller voyage Europe. Propose des itinéraires réalistes, budgets estimés, transports, "
     "conseils saisonniers et bonnes pratiques locales.",
     None),
    ("Chef pâtissier",
     "Tu es Chef pâtissier. Recettes précises (g, °C, minutes), techniques (cristallisation, émulsions) "
     "et astuces d'organisation. Propose des variantes et substitutions.",
     None),
]

def insert_users(conn):
    inserted = 0
    with conn.cursor() as cur:
        cur.execute("SET search_path TO projetgpt;")
        for prenom, nom, mail, mdp, naiss in USERS:
            mail_norm = (mail or "").strip().lower()
            mdp_hache = hash_pwd(mdp, mail_norm)  # même sel que côté login
            cur.execute(
                """
                INSERT INTO utilisateur (prenom, nom, mail, mdp, naiss)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (mail) DO NOTHING
                """,
                (prenom, nom, mail_norm, mdp_hache, naiss),
            )
            inserted += cur.rowcount  # 1 si inséré, 0 si déjà présent
    conn.commit()
    return inserted

def insert_personnages(conn):
    inserted = 0
    with conn.cursor() as cur:
        # éviter les doublons par name (pas d'unique dans le DDL) : upsert manuel
        for name, system_prompt, created_by in PERSONNAGES:
            cur.execute(
                """
                INSERT INTO personnageIA (name, system_prompt, created_by)
                SELECT %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM personnageIA WHERE name = %s
                )
                """,
                (name, system_prompt, created_by, name),
            )
            inserted += cur.rowcount
    conn.commit()
    return inserted

def main():
    conn = DBConnection().connection
    u = insert_users(conn)
    p = insert_personnages(conn)
    print(f"Utilisateurs insérés: {u} / {len(USERS)}")
    print(f"Personnages insérés:  {p} / {len(PERSONNAGES)}")

if __name__ == "__main__":
    main()
