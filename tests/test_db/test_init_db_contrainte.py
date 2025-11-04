import pytest
import psycopg2
import datetime
import time

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
        '''Vérification que si l'on supprime un utlisateur ses conversations et sessions sont aussi supprimés'''
        # Création de l'utilisateur et d'une conversation et session
        self.cur.execute(f"""
            INSERT INTO {self.schema}.utilisateur (prenom, nom, mail, mdp) VALUES ('Clara','C','clara.C@mail.com', 'mdp') RETURNING id_utilisateur;
        """)
        id_user = self.cur.fetchone()[0]

        self.cur.execute(f"""
            INSERT INTO {self.schema}.session (id_utilisateur) VALUES (%s);
        """, (id_user,))

        self.cur.execute(f"""
            INSERT INTO {self.schema}.personnageIA (name, system_prompt) 
            VALUES ('Cuisinier', 'Tu es comme un chef')
            RETURNING id_personnageIA;
        """)
        id_persoIA = self.cur.fetchone()[0]

        self.cur.execute(f"""
            INSERT INTO {self.schema}.conversation (id_proprio, id_personnageIA) VALUES (%s, %s);
        """, (id_user, id_persoIA))

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
        """Vérifie que le trigger updated_at se déclenche sur utilisateur"""
        # Création d'un utilisateur
        self.cur.execute(f"""
            INSERT INTO {self.schema}.utilisateur (prenom, nom, mail, mdp) 
            VALUES ('Clara', 'C', 'clara.C@mail.com', 'mdp')
            RETURNING id_utilisateur, updated_at;
        """)
        id_utilisateur, premier_temps = self.cur.fetchone()

        # Attente pour garantir un timestamp différent
        time.sleep(1)

        # Mise à jour du mail (avec valeur unique)
        nouveau_mail = f"clara{int(time.time())}@mail.com"
        self.cur.execute(f"""
            UPDATE {self.schema}.utilisateur
            SET mail = %s
            WHERE id_utilisateur = %s
            RETURNING updated_at;
        """, (nouveau_mail, id_utilisateur))
        deuxieme_temps = self.cur.fetchone()[0]

        assert deuxieme_temps > premier_temps, "Le trigger 'set_updated_at' n'a pas été exécuté sur utilisateur."


    def test_trigger_updates_timestamp_conversation(self):
        """Vérifie que le trigger updated_at se déclenche sur conversation"""
        # Création d’un personnage IA (clé étrangère requise)
        self.cur.execute(f"""
            INSERT INTO {self.schema}.personnageIA (name, system_prompt)
            VALUES ('Cuisinier', 'Je réponds comme un chef')
            RETURNING id_personnageIA;
        """)
        id_perso = self.cur.fetchone()[0]

        # Création d’un utilisateur (clé étrangère pour conversation)
        self.cur.execute(f"""
            INSERT INTO {self.schema}.utilisateur (prenom, nom, mail, mdp)
            VALUES ('Alice', 'A', 'alice{int(time.time())}@mail.com', 'mdp')
            RETURNING id_utilisateur;
        """)
        id_user = self.cur.fetchone()[0]

        # Création d'une conversation
        self.cur.execute(f"""
            INSERT INTO {self.schema}.conversation (id_proprio, id_personnageIA)
            VALUES (%s, %s)
            RETURNING id_conversation, updated_at;
        """, (id_user, id_perso))
        id_conversation, premier_temps = self.cur.fetchone()

        time.sleep(1)

        # Mise à jour de la conversation
        self.cur.execute(f"""
            UPDATE {self.schema}.conversation
            SET titre = 'Nouvelle conversation test'
            WHERE id_conversation = %s
            RETURNING updated_at;
        """, (id_conversation,))
        deuxieme_temps = self.cur.fetchone()[0]

        assert deuxieme_temps > premier_temps, "Le trigger 'set_updated_at' n'a pas été exécuté sur conversation."


    def test_trigger_updates_timestamp_personnageIA(self):
        """Vérifie que le trigger updated_at se déclenche sur personnageIA"""
        # Création d'un personnage IA
        self.cur.execute(f"""
            INSERT INTO {self.schema}.personnageIA (name, system_prompt)
            VALUES ('Cuisinier', 'Test')
            RETURNING id_personnageIA, updated_at;
        """)
        id_personnageIA, premier_temps = self.cur.fetchone()

        time.sleep(1)

        # Mise à jour du nom
        self.cur.execute(f"""
            UPDATE {self.schema}.personnageIA
            SET name = 'Professeur'
            WHERE id_personnageIA = %s
            RETURNING updated_at;
        """, (id_personnageIA,))
        deuxieme_temps = self.cur.fetchone()[0]

        assert deuxieme_temps > premier_temps, "Le trigger 'set_updated_at' n'a pas été exécuté sur personnageIA."

    def test_default_timestamps(self):
        """Vérification que created_at et updated_at de la table utilisateur 
        sont bien initialisés automatiquement"""
        self.cur.execute("""
            INSERT INTO projetGPT.utilisateur (prenom, nom, mail, mdp)
            VALUES ('Clara', 'C', 'default@mail.com', 'mdp')
            RETURNING created_at, updated_at;
        """)
        created_at, updated_at = self.cur.fetchone()
        assert created_at and updated_at, "Les champs created_at / updated_at n'ont pas été remplis automatiquement."
        assert isinstance(created_at, datetime.datetime)
        assert isinstance(updated_at,datetime.datatime)