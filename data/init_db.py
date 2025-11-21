import os

import psycopg2

try:
    import dotenv

    dotenv.load_dotenv(override=True)
except Exception:
    pass

PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
PG_DB = os.getenv("POSTGRES_DATABASE", "postgres")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PWD = os.getenv("POSTGRES_PASSWORD", "postgres")
SCHEMA = os.getenv("POSTGRES_SCHEMA", "projetGPT")


DDL = f"""
CREATE SCHEMA IF NOT EXISTS {SCHEMA};
SET search_path TO {SCHEMA};

-- ================================
-- Table : UTILISATEUR
-- ================================
CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur   SERIAL PRIMARY KEY,
    prenom           VARCHAR(100) NOT NULL,
    nom              VARCHAR(100) NOT NULL,
    mail             VARCHAR(255) NOT NULL UNIQUE,
    mdp              TEXT NOT NULL,
    naiss            DATE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ================================
-- Table : PERSONNAGE IA
-- ================================
CREATE TABLE IF NOT EXISTS personnageIA (
    id_personnageIA SERIAL PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    system_prompt  TEXT NOT NULL,
    created_by     INTEGER REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (name, created_by)
);

-- ================================
-- Table : SESSION
-- ================================
CREATE TABLE IF NOT EXISTS session (
    id_session     SERIAL PRIMARY KEY,
    id_utilisateur INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at       TIMESTAMPTZ DEFAULT NULL
);

-- ================================
-- Table : CONVERSATION
-- ================================
CREATE TABLE IF NOT EXISTS conversation (
    id_conversation SERIAL PRIMARY KEY,
    id_proprio      INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_personnageIA INTEGER NOT NULL REFERENCES personnageIA(id_personnageIA),
    titre           VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature     REAL,
    top_p           REAL,
    max_tokens      INTEGER NOT NULL DEFAULT 1000,
    is_collab       BOOLEAN DEFAULT FALSE,
    token_collab    VARCHAR(16)
);

-- ================================
-- Table : MESSAGE
-- ================================
CREATE TABLE IF NOT EXISTS message (
    id_message      SERIAL PRIMARY KEY,
    id_conversation INTEGER NOT NULL REFERENCES conversation(id_conversation) ON DELETE CASCADE,
    expediteur      VARCHAR(16) NOT NULL CHECK (expediteur IN ('utilisateur','IA')),
    id_utilisateur  INTEGER REFERENCES utilisateur(id_utilisateur),
    contenu         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ================================
-- Table d’association : utilisateur - conversation
-- ================================
CREATE TABLE IF NOT EXISTS conv_utilisateur (
    id_utilisateur   INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_conversation  INTEGER NOT NULL REFERENCES conversation(id_conversation) ON DELETE CASCADE,
    PRIMARY KEY (id_utilisateur, id_conversation)
);
-- ================================
-- Index
-- ================================
DROP INDEX IF EXISTS idx_utilisateur_mail;
CREATE INDEX idx_utilisateur_mail ON utilisateur(mail);

DROP INDEX IF EXISTS idx_session_user;
CREATE INDEX idx_session_user ON session(id_utilisateur);

DROP INDEX IF EXISTS idx_conversation_personnageIA;
CREATE INDEX idx_conversation_personnageIA ON conversation(id_personnageIA);

DROP INDEX IF EXISTS idx_message_conversation_time;
CREATE INDEX idx_message_conversation_time ON message(id_conversation, created_at);

DROP INDEX IF EXISTS idx_conversation_proprio;
CREATE INDEX idx_conversation_proprio ON conversation(id_proprio);

DROP INDEX IF EXISTS idx_conv_utilisateur_user;
CREATE INDEX idx_conv_utilisateur_user ON conv_utilisateur(id_utilisateur);

DROP INDEX IF EXISTS idx_conv_utilisateur_conversation;
CREATE INDEX idx_conv_utilisateur_conversation ON conv_utilisateur(id_conversation);

DROP INDEX IF EXISTS idx_persoia_utilisateur_user;
CREATE INDEX idx_persoia_utilisateur_user ON personnageIA(created_by);

DROP INDEX IF EXISTS idx_persoia_utilisateur_perso;
CREATE INDEX idx_persoia_utilisateur_perso ON personnageIA(id_personnageIA);

-- ================================
-- Trigger : mise à jour automatique de updated_at
-- ================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = clock_timestamp();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS utilisateur_set_updated_at ON utilisateur;
CREATE TRIGGER utilisateur_set_updated_at
BEFORE UPDATE ON utilisateur
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

DROP TRIGGER IF EXISTS conversation_set_updated_at ON conversation;
CREATE TRIGGER conversation_set_updated_at
BEFORE UPDATE ON conversation
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

DROP TRIGGER IF EXISTS personnageIA_set_updated_at ON personnageIA;
CREATE TRIGGER personnageIA_set_updated_at
BEFORE UPDATE ON personnageIA
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

"""


def ensure_database_exists():
    admin_conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname="postgres", user=PG_USER, password=PG_PWD
    )
    admin_conn.autocommit = True
    with admin_conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (PG_DB,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{PG_DB}";')
            print(f"Base `{PG_DB}` créée.")
    admin_conn.close()


def main():
    ensure_database_exists()
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PWD
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(DDL)
        print(f"Base/Schéma initialisés dans `{SCHEMA}` (DB `{PG_DB}`).")
    conn.close()


if __name__ == "__main__":
    main()
