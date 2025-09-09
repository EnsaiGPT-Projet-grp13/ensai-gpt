# init_db.py — corrige les références vers personageIA(id_personageIA)
import os
import psycopg2

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
SCHEMA  = os.getenv("POSTGRES_SCHEMA", "projetGPT")  # lira ta valeur depuis .env

DDL = f"""
CREATE SCHEMA IF NOT EXISTS {SCHEMA};
SET search_path TO {SCHEMA};

-- Utilisateur
CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur   SERIAL PRIMARY KEY,
    prenom           VARCHAR(100) NOT NULL,
    nom              VARCHAR(100) NOT NULL,
    mail             VARCHAR(255) NOT NULL UNIQUE,
    mdp              TEXT NOT NULL,
    naiss            DATE NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Personnage IA (gardons ton nom de table/colonnes)
CREATE TABLE IF NOT EXISTS personageIA (
    id_personageIA VARCHAR(64) PRIMARY KEY,
    name           VARCHAR(100) NOT NULL UNIQUE,
    system_prompt  TEXT NOT NULL
);

-- Session de chat
CREATE TABLE IF NOT EXISTS chat_session (
    id_session       SERIAL PRIMARY KEY,
    id_utilisateur   INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_personageIA   VARCHAR(64) REFERENCES personageIA(id_personageIA),
    started_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at         TIMESTAMPTZ NULL
);

-- Messages
CREATE TABLE IF NOT EXISTS chat_message (
    id_message  SERIAL PRIMARY KEY,
    id_session  INTEGER NOT NULL REFERENCES chat_session(id_session) ON DELETE CASCADE,
    sender      VARCHAR(16) NOT NULL CHECK (sender IN ('user','ai','system')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index
DROP INDEX IF EXISTS idx_utilisateur_mail;
CREATE INDEX idx_utilisateur_mail ON utilisateur(mail);

DROP INDEX IF EXISTS idx_session_user;
CREATE INDEX idx_session_user ON chat_session(id_utilisateur);

DROP INDEX IF EXISTS idx_session_personageIA;
CREATE INDEX idx_session_personageIA ON chat_session(id_personageIA);

DROP INDEX IF EXISTS idx_message_session_time;
CREATE INDEX idx_message_session_time ON chat_message(id_session, created_at);

-- Trigger de mise à jour du updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS utilisateur_set_updated_at ON utilisateur;
CREATE TRIGGER utilisateur_set_updated_at
BEFORE UPDATE ON utilisateur
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
"""

def main():
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PWD
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(DDL)
            print(f"Base/Schéma initialisés dans `{SCHEMA}`.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
