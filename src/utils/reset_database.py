import logging
import os
from unittest import mock

import dotenv

from dao.db import DBConnection
from service.utilisateur_service import UtilisateurService
from utils.log_decorator import log
from utils.singleton import Singleton


class ResetDatabase(metaclass=Singleton):
    """
    Réinitialisation de la base de données (schéma + données).
    """

    @log
    def lancer(self, test_dao: bool = False):
        """
        Lancement de la réinitialisation des données.
        Si test_dao = True : réinitialisation avec les données de TEST.
        """
        if test_dao:
            # Force le schéma de test
            mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}).start()
            pop_data_path = "data/pop_db_test.sql"
        else:
            pop_data_path = "data/pop_db.sql"

        # Charger les variables d'environnement (.env)
        dotenv.load_dotenv()

        schema = os.environ["POSTGRES_SCHEMA"]

        create_schema = f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"

        with open("data/init_db.sql", encoding="utf-8") as f:
            init_db_as_string = f.read()

        with open(pop_data_path, encoding="utf-8") as f:
            pop_db_as_string = f.read()

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(create_schema)
                    cursor.execute(init_db_as_string)
                    cursor.execute(pop_db_as_string)
        except Exception as e:
            logging.info(e)
            raise

        # Appliquer le hashage des mots de passe à chaque utilisateur
        utilisateur_service = UtilisateurService()
        for u in utilisateur_service.lister_tous(inclure_mdp=True):
            utilisateur_service.modifier(u)

        return True


if __name__ == "__main__":
    ResetDatabase().lancer()
    ResetDatabase().lancer(True)
