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
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature      REAL,
    top_p            REAL,
    max_tokens       INTEGER NOT NULL    
);

-- Personna IA 
CREATE TABLE IF NOT EXISTS personnageIA (
    id_personnageIA SERIAL PRIMARY KEY,
    name           VARCHAR(100) NOT NULL UNIQUE,
    system_prompt  TEXT NOT NULL,
    created_by     INTEGER REFERENCES utilisateur(id_utilisateur),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Session
CREATE TABLE IF NOT EXISTS session (
    id_session       SERIAL PRIMARY KEY,
    id_utilisateur   INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    started_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at         TIMESTAMPTZ NULL
);

-- Conversation
CREATE TABLE IF NOT EXISTS conversation (
    id_conversation       SERIAL PRIMARY KEY,
    id_proprio            INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_personnageIA       INTEGER NOT NULL REFERENCES personnageIA(id_personnageIA),
    titre                 VARCHAR(64),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature           REAL,
    top_p                 REAL,
    max_tokens            INTEGER NOT NULL,
    is_collab             BOOLEAN,
    token_collab          VARCHAR(16)
);

-- Messages
CREATE TABLE IF NOT EXISTS message (
    id_message       SERIAL PRIMARY KEY,
    id_conversation  INTEGER NOT NULL REFERENCES conversation(id_conversation) ON DELETE CASCADE,
    expediteur       VARCHAR(16) NOT NULL CHECK (expediteur IN ('utilisateur','IA')),
    id_utilisateur   INTEGER REFERENCES utilisateur(id_utilisateur),
    contenu          TEXT NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conversations utilisateurs, table d'association
CREATE TABLE IF NOT EXISTS conv_utilisateur (
    id_utilisateur   INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_conversation  INTEGER NOT NULL REFERENCES conversation(id_conversation) ON DELETE CASCADE,
    PRIMARY KEY (id_utilisateur, id_conversation)
);

-- Personnages IA utilisateurs, table d'association
CREATE TABLE IF NOT EXISTS persoIA_utilisateur (
    id_utilisateur   INTEGER NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    id_personnageIA  INTEGER NOT NULL REFERENCES personnageIA(id_personnageIA) ON DELETE CASCADE,
    PRIMARY KEY (id_utilisateur, id_personnageIA)
);

-- Index, permet à la db de retrouver plus vite certains éléments 
-- sans devoir parcourir toute la table
-- Pour l'authentification et vérifier l'unicité du mail
DROP INDEX IF EXISTS idx_utilisateur_mail;
CREATE INDEX idx_utilisateur_mail ON utilisateur(mail);

-- Pour retrouver toutes les sessions d'un utilisateur
DROP INDEX IF EXISTS idx_session_user;
CREATE INDEX idx_session_user ON session(id_utilisateur);

-- Pour retrouver toutes les conversations d'un personnageIA
DROP INDEX IF EXISTS idx_conversation_personnageIA;
CREATE INDEX idx_conversation_personnageIA ON conversation(id_personnageIA);

-- Pour retrouver tous les personnages IA d'un utilisateur
DROP INDEX IF EXISTS idx_utilisateur_personnageIA;
CREATE INDEX idx_utilisateur_personnageIA ON personnageIA(id_personnageIA);

-- Pour obtenir les message d'une conversation dans l'ordre
DROP INDEX IF EXISTS idx_message_conversation_time;
CREATE INDEX idx_message_conversation_time ON message(id_conversation, created_at);

-- Pour retrouver les conversations dont un utilisateur est propriétaire
DROP INDEX IF EXISTS idx_conversation_proprio;
CREATE INDEX idx_conversation_proprio ON conversation(id_proprio);

-- Table d'association : pour rechercher rapidement par utilisateur ou par conversation
DROP INDEX IF EXISTS idx_conv_utilisateur_user;
CREATE INDEX idx_conv_utilisateur_user ON conv_utilisateur(id_utilisateur);

DROP INDEX IF EXISTS idx_conv_utilisateur_conversation;
CREATE INDEX idx_conv_utilisateur_conversation ON conv_utilisateur(id_conversation);

-- Table d'association : pour rechercher rapidement par utilisateur ou par personnage IA
DROP INDEX IF EXISTS idx_persoIA_utilisateur_user;
CREATE INDEX idx_persoIA_utilisateur_user ON persoIA_utilisateur(id_utilisateur);

DROP INDEX IF EXISTS idx_persoIA_utilisateur_perso;
CREATE INDEX idx_persoIA_utilisateur_perso ON persoIA_utilisateur(id_personnageIA);

-- Trigger : permet d'automatiser certaines actions dans la db
-- Trigger de mise à jour du updated_at, à chaque modification la date change automatiquement
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

DROP TRIGGER IF EXISTS conversation_set_updated_at ON conversation;
CREATE TRIGGER conversation_set_updated_at
BEFORE UPDATE ON conversation
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

DROP TRIGGER IF EXISTS personnageIA_set_updated_at ON personnageIA;
CREATE TRIGGER personnageIA_set_updated_at
BEFORE UPDATE ON personnageIA
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