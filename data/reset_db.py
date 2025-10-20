import psycopg2
from data import init_db

def reset_database():
    '''Réinitialisation des bases de données'''
    conn = psycopg2.connect(
        host=init_db.PG_HOST,
        port=init_db.PG_PORT,
        dbname=init_db.PG_DB,
        user=init_db.PG_USER,
        password=init_db.PG_PWD
    )
    conn.autocommit = True
    cur = conn.cursor()

    """Suppression du schéma existant"""
    cur.execute("DROP SCHEMA IF EXISTS projetgpt CASCADE;")

    """Réinitialisation du schéma"""
    with open("data/init_db.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()
    cur.execute(sql_script)

    cur.close()
    conn.close()
    print("Les bases de données ont été réinitialisées")

if __name__ == "__main__":
    reset_database()