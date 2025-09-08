# --- place ces 2 lignes tout en haut, avant tout import psycopg2 ---
import os
os.environ["PGCLIENTENCODING"] = "UTF8"   # force l'encodage côté libpq

import dotenv
dotenv.load_dotenv(override=True)

import psycopg2

def main():
    try:
        conn = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            dbname=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            # double ceinture & bretelles :
            options="-c client_encoding=UTF8",
            # utile sur certains serveurs scolaires :
            sslmode="prefer",
            connect_timeout=5,
        )
        with conn.cursor() as cur:
            cur.execute("SHOW server_encoding;")
            print("server_encoding:", cur.fetchone()[0])

            schema = os.environ.get("POSTGRES_SCHEMA", "public")
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name;
            """, (schema,))
            rows = cur.fetchall()
            if rows:
                print(f"✅ Tables dans le schéma {schema}:")
                for (t,) in rows:
                    print(" -", t)
            else:
                print(f"⚠️  Aucune table trouvée dans le schéma {schema}.")
        conn.close()
    except Exception as e:
        # Affichage safe même si l'encodage du message est foireux
        print("❌ Erreur de connexion :", repr(e))

if __name__ == "__main__":
    main()
