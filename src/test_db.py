# test_connexion.py
from dao.db_connection import DBConnection
try:
    with DBConnection().connection as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database() AS db, current_schema() AS sch;")
            print(cur.fetchone())
except Exception as e:
    print("❌ Erreur de connexion :", e)
