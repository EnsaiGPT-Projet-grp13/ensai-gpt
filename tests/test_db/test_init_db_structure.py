import pytest
import psycopg2
import os
import sys

from data import init_db

class TestStructureDB():
    @classmethod
    def setup_class(cls):
        """Créé une connexion unique qui sera utilisée par tous les tests"""
        cls.conn = psycopg2.connect(
            host=init_db.PG_HOST,
            port=init_db.PG_PORT,
            dbname=init_db.PG_DB,
            user=init_db.PG_USER,
            password=init_db.PG_PWD
        )
        cls.conn.autocommit = True
        cls.cur = cls.conn.cursor()

    @classmethod
    def teardown_class(cls):
        """Ferme la connexion unique après l'exécution tous les tests"""
        cls.cur.close()
        cls.conn.close()

    ### Tests d'existence
    def test_schema_existe(self):
        """Vérifie que le schéma projetGPT existe bien"""
        self.cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name='projetgpt';")
        assert self.cur.fetchone(), "Le schéma 'projetGPT' n'existe pas"


    def test_tables_existent(self):
        """Vérifie que toutes les tables ont bien été créées"""
        tables_attendues = {
            'utilisateur', 'personnageia', 'session', 'conversation',
            'message', 'conv_utilisateur', 'persoia_utilisateur'
        }
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='projetgpt';")
        tables_existantes = {table[0] for table in self.cur.fetchall()}
        manquantes = tables_attendues - tables_existantes
        assert not manquantes, f"Il manque les tables suivantes : {manquantes}"

    def test_idex_existent(self):
        """Vérifie que tous les index attendus ont été créés"""
        index_attendus = {
            'idx_utilisateur_mail',
            'idx_session_user',
            'idx_conversation_personnageia',
            'idx_utilisateur_personnageia',
            'idx_message_conversation_time',
            'idx_conversation_proprio',
            'idx_conv_utilisateur_user',
            'idx_conv_utilisateur_conversation',
            'idx_persoia_utilisateur_user',
            'idx_persoia_utilisateur_perso'
        }

        self.cur.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'projetgpt';
        """)
        index_existants = {index[0] for index in self.cur.fetchall()}
        manquants = index_attendus - index_existants
        assert not manquants, f"Ils manquent les index suivants : {manquants}"


    def test_colonnes_utilisateur(self):
        """Vérifie que les colonnes importantes de 'utilisateur' existent"""
        self.cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='projetgpt' AND table_name='utilisateur';
        """)
        colonnes_existantes = {colonne[0] for colonne in self.cur.fetchall()}
        attendues = {'id_utilisateur', 'mail', 'mdp'}
        manquantes = attendues - colonnes_existantes
        assert not manquantes, f"Colonnes manquantes dans utilisateur : {manquantes}"


    def test_colonnes_personnageIA(self):
        """Vérifie que les colonnes importantes de 'personnageIA' existent"""
        self.cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='projetgpt' AND table_name='personnageia';
        """)
        colonnes_existantes = {colonne[0] for colonne in self.cur.fetchall()}
        attendues = {'id_personnageia', 'name', 'system_prompt'}
        manquantes = attendues - colonnes_existantes
        assert not manquantes, f"Colonnes manquantes dans personnageIA : {manquantes}"


    def test_colonnes_session(self):
        """Vérifie que les colonnes importantes de 'session' existent"""
        self.cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='projetgpt' AND table_name='session';
        """)
        colonnes_existantes = {colonne[0] for colonne in self.cur.fetchall()}
        attendues = {'id_session', 'id_utilisateur'}
        manquantes = attendues - colonnes_existantes
        assert not manquantes, f"Colonnes manquantes dans session : {manquantes}"


    def test_colonnes_conversation(self):
        """Vérifie que les colonnes importantes de 'conversation' existent"""
        self.cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='projetgpt' AND table_name='conversation';
        """)
        colonnes_existantes = {colonne[0] for colonne in self.cur.fetchall()}
        attendues = {'id_conversation', 'id_proprio', 'id_personnageia', 'titre'}
        manquantes = attendues - colonnes_existantes
        assert not manquantes, f"Colonnes manquantes dans conversation : {manquantes}"


    def test_colonnes_message(self):
        """Vérifie que les colonnes importantes de 'message' existent"""
        self.cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='projetgpt' AND table_name='message';
        """)
        colonnes_existantes = {colonne[0] for colonne in self.cur.fetchall()}
        attendues = {'id_message', 'id_conversation', 'contenu'}
        manquantes = attendues - colonnes_existantes
        assert not manquantes, f"Colonnes manquantes dans message : {manquantes}"


    def test_colonnes_conv_utilisateur(self):
        """Vérifie que les colonnes importantes de 'conv_utilisateur' existent"""
        self.cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='projetgpt' AND table_name='conv_utilisateur';
        """)
        colonnes_existantes = {colonne[0] for colonne in self.cur.fetchall()}
        attendues = {'id_utilisateur', 'id_conversation'}
        manquantes = attendues - colonnes_existantes
        assert not manquantes, f"Colonnes manquantes dans conv_utilisateur : {manquantes}"


    def test_colonnes_persoIA_utilisateur(self):
        """Vérifie que les colonnes importantes de 'persoIA_utilisateur' existent"""
        self.cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='projetgpt' AND table_name='persoia_utilisateur';
        """)
        colonnes_existantes = {colonne[0] for colonne in self.cur.fetchall()}
        attendues = {'id_utilisateur', 'id_personnageia'}
        manquantes = attendues - colonnes_existantes
        assert not manquantes, f"Colonnes manquantes dans persoIA_utilisateur : {manquantes}"

    
