import os
import sys
from unittest import mock
from unittest.mock import patch

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from dao.utilisateur_dao import UtilisateurDao
from objects.utilisateur import Utilisateur
from utils.securite import hash_password

@pytest.fixture(scope="session", autouse=True)
def environnement_tests():
    """
    - Force l'utilisation d'un schéma de BDD (projetGPT par défaut).
    - Mock ResetDatabase.lancer pour ne pas tenter de lire un SQL ou
      réinitialiser la base pendant les tests.
    """
    schema = os.getenv("POSTGRES_SCHEMA", "projetGPT")

