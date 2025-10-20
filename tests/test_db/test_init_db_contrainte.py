import pytest
import psycopg2

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
            'utilisateur', 'personnageIA', 'session', 'conversation',
            'message', 'conv_utilisateur', 'persoIA_utilisateur'
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
            INSERT INTO {self.schema}.utilisateur (mail, mdp)
            VALUES ('clara.C@mail.com', 'claramdp');
        """)
        with pytest.raises(psycopg2.errors.UniqueViolation):
            self.cur.execute(f"""
                INSERT INTO {self.schema}.utilisateur (mail, mdp)
                VALUES ('clara.C@mail.com', 'mdp');
            """)

    ### Tests des ON DELETE CASCADE sur les clés étrangères
    def test_fk_on_delete_cascade(self):
        '''Vérification que ci l'on supprime un utlisateur ses conversations et sessions sont aussi supprimés'''
        # Création de l'utilisateur et d'une conversation et session
        self.cur.execute(f"""
            INSERT INTO {self.schema}.utilisateur (mail, mdp) VALUES ('clara.C@mail.com', 'mdp') RETURNING id_utilisateur;
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