import pytest
import psycopg2
import datetime

from data import init_db

class TestContraintesDB():
    @classmethod
    def setup_class(cls):
        '''Création de la connexion à PostGre et du curseur pour les tests de la classe'''
        cls.conn = psycopg2.connect(
            host=init_db.PG_HOST,
            port=init_db.PG_PORT,
            dbname=init_db.PG_DB,
            user=init_db.PG_USER,
            password=init_db.PG_PWD
        )
        cls.conn.autocommit = False
        cls.cur = cls.conn.cursor()
        cls.schema = 'projetgpt'

    @classmethod
    def teardown_class(cls):
        '''Fermeture de la connection et du curseur avec chaque test'''
        cls.cur.close()
        cls.conn.close()

    def setup_method(self):
        '''Sauvegarde de l'état des databases avant chacun des tests indépendants'''
        self.cur.execute("SAVEPOINT test_savepoint;")

    def teardown_method(self):
        '''Retour à l'état précédent le test, au Savepoint'''
        self.cur.execute("ROLLBACK TO SAVEPOINT test_savepoint;")

    ### Tests des clés primaires
    def test_cles_primaires(self):
        """Vérification que les clés sont bien des clés primaires"""
        tables = [
            'utilisateur', 'personnageia', 'session', 'conversation',
            'message', 'conv_utilisateur', 'persoia_utilisateur'
        ]
        for table in tables:
            self.cur.execute(f"""
                SELECT COUNT(*) FROM information_schema.table_constraints
                WHERE table_schema = %s
                  AND table_name = %s
                  AND constraint_type = 'PRIMARY KEY';
            """, (self.schema, table))
            assert self.cur.fetchone()[0] == 1, f"Attention la table {table} ne possède pas de clés primaires"

    ### Test des contraintes d'unicité
    def test_mail_utilisateur_unique(self):
        '''Test si une erreur est bien signalée si on met deux fois le même mail'''
        self.cur.execute(f"""
            INSERT INTO {self.schema}.utilisateur (prenom, nom, mail, mdp)
            VALUES ('Clara','C','clara.C@mail.com', 'claramdp');
        """)
        with pytest.raises(psycopg2.errors.UniqueViolation):
            self.cur.execute(f"""
                INSERT INTO {self.schema}.utilisateur (prenom, nom, mail, mdp)
                VALUES ('Clara','C','clara.C@mail.com', 'mdp');
            """)

    ### Tests des ON DELETE CASCADE sur les clés étrangères
    def test_fk_on_delete_cascade(self):
        '''Vérification que ci l'on supprime un utlisateur ses conversations et sessions sont aussi supprimés'''
        # Création de l'utilisateur et d'une conversation et session
        self.cur.execute(f"""
            INSERT INTO {self.schema}.utilisateur (prenom, nom, mail, mdp) VALUES ('Clara','C','clara.C@mail.com', 'mdp') RETURNING id_utilisateur;
        """)
        id_user = self.cur.fetchone()[0]

        self.cur.execute(f"""
            INSERT INTO {self.schema}.session (id_utilisateur) VALUES (%s);
        """, (id_user,))

        self.cur.execute(f"""
            INSERT INTO {self.schema}.conversation (id_proprio) VALUES (%s);
        """, (id_user,))

        # Suppression de l'utilisateur
        self.cur.execute(f"""
            DELETE FROM {self.schema}.utilisateur WHERE id_utilisateur = %s;
        """, (id_user,))

        # Vérification que la session et conversation sont bien supprimées
        self.cur.execute(f"SELECT * FROM {self.schema}.session WHERE id_utilisateur = %s", (id_user,))
        assert self.cur.fetchone() is None

        self.cur.execute(f"SELECT * FROM {self.schema}.conversation WHERE id_proprio = %s", (id_user,))
        assert self.cur.fetchone() is None

    ### Tests des triggers 
    def test_trigger_updates_timestamp_utilisateur(self):
        """Vérification qu'une modification met bien à jour le trigger updated_at"""
        # Creation d'un utilisateur
        self.cur.execute(f"""
            INSERT INTO {self.schema}.utilisateur (prenom, nom, mail, mdp) VALUES ('Clara','C','clara.C@mail.com', 'mdp') RETURNING id_utilisateur, updated_at;
        """)
        id_utilisateur, premier_temps = self.cur.fetchone()

        # Attente que le temps passe un peu
        import time; time.sleep(1)

        # Mise à jour du mail
        self.cur.execute("""
            UPDATE projetGPT.utilisateur
            SET mail='clara.C2@mail.com'
            WHERE id_utilisateur=%s
            RETURNING updated_at;
        """, (id_utilisateur,))
        deuxieme_temps = self.cur.fetchone()[0]

        assert premier_temps > deuxieme_temps, "Attention le trigger 'set_updated_at' ne met pas à jour le timestamp."

    def test_trigger_updates_timestamp_conversation(self):
        """Vérification qu'une modification met bien à jour le trigger updated_at"""
        # Creation d'une conversation
        self.cur.execute(f"""
            INSERT INTO {self.schema}.conversation (id_conversation, id_proprio, id_personnageIA) VALUES (1,1,1) RETURNING id_conversation, updated_at;
        """)
        id_conversation, premier_temps = self.cur.fetchone()

        # Attente que le temps passe un peu
        import time; time.sleep(1)

        # Mise à jour du personnage IA
        self.cur.execute("""
            UPDATE projetgpt.conversation
            SET id_personnageIA = 2
            WHERE id_conversation=%s
            RETURNING updated_at;
        """, (id_conversation,))
        deuxieme_temps = self.cur.fetchone()[0]

        assert premier_temps > deuxieme_temps, "Attention le trigger 'set_updated_at' ne met pas à jour le timestamp."

    def test_trigger_updates_timestamp_personnageIA(self):
        """Vérification qu'une modification met bien à jour le trigger updated_at"""
        # Creation d'un personnage IA
        self.cur.execute(f"""
            INSERT INTO {self.schema}.personnageIA (id_personnageIA, name, system_prompt) VALUES (1,'Cuisinier','Test') RETURNING id_personnageIA, updated_at;
        """)
        id_personnageIA, premier_temps = self.cur.fetchone()

        # Attente que le temps passe un peu
        import time; time.sleep(1)

        # Mise à jour du personnage IA
        self.cur.execute("""
            UPDATE projetgpt.id_personnageIA
            SET name = "professeur"
            WHERE id_conversation=%s
            RETURNING updated_at;
        """, (id_personnageIA,))
        deuxieme_temps = self.cur.fetchone()[0]

        assert premier_temps > deuxieme_temps, "Attention le trigger 'set_updated_at' ne met pas à jour le timestamp."

    def test_default_timestamps(self):
        """Vérification que created_at et updated_at sont bien initialisés automatiquement"""
        self.cur.execute("""
            INSERT INTO projetGPT.utilisateur (prenom, nom, mail, mdp)
            VALUES ('Clara', 'C', 'default@mail.com', 'mdp')
            RETURNING created_at, updated_at;
        """)
        created_at, updated_at = self.cur.fetchone()
        assert created_at and updated_at, "Les champs created_at / updated_at n'ont pas été remplis automatiquement."
        assert isinstance(created_at, datetime.datetime)