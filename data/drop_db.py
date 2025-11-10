import os
import psycopg2
from psycopg2 import sql

try:
    import dotenv
    dotenv.load_dotenv(override=True)
except Exception:
    pass

PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
PG_DB   = os.getenv("POSTGRES_DATABASE", "postgres")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PWD  = os.getenv("POSTGRES_PASSWORD", "postgres")

def drop_database():
    # Connexion à la base par défaut "postgres" pour pouvoir supprimer l’autre
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname="postgres", user=PG_USER, password=PG_PWD
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        print(f"Suppression complète de la base `{PG_DB}`...")
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(PG_DB)))
        print(f"Base `{PG_DB}` supprimée avec succès.")
    conn.close()

if __name__ == "__main__":
    drop_database()
