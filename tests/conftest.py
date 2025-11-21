# tests/conftest.py
import os
import sys
from unittest import mock
from unittest.mock import patch

import pytest

# === Imports du projet ===
from dao.utilisateur_dao import UtilisateurDao
from objects.utilisateur import Utilisateur
from utils.reset_database import ResetDatabase
from utils.securite import hash_password

# === Ajouter src/ au PYTHONPATH ===
THIS_DIR = os.path.dirname(__file__)  # .../ensai-gpt/tests
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))  # .../ensai-gpt
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


@pytest.fixture(scope="session", autouse=True)
def environnement_tests():
    """
    - Force l'utilisation d'un schéma de BDD (projetGPT par défaut).
    - Mock ResetDatabase.lancer pour ne pas tenter de lire un SQL ou
      réinitialiser la base pendant les tests.
    """
    schema = os.getenv("POSTGRES_SCHEMA", "projetGPT")

    with patch.dict(os.environ, {"SCHEMA": schema}):
        # ResetDatabase.lancer ne fait plus rien, retourne juste True.
        with mock.patch.object(ResetDatabase, "lancer", return_value=True):
            yield


@pytest.fixture
def utilisateur_existant():
    """
    Crée un utilisateur en BDD et le retourne.
    Si un utilisateur avec le même mail existe déjà, il est supprimé puis recréé.
    """
    mail = "alice@test.com"
    dao = UtilisateurDao()

    if dao.exists_mail(mail):
        u_old = dao.find_by_mail(mail)
        dao.delete(u_old.id_utilisateur)

    u = Utilisateur(
        id_utilisateur=None,
        prenom="Alice",
        nom="Test",
        mdp_hash=hash_password("mdpAlice", mail),
        naiss="2000-01-01",
        mail=mail,
    )
    created = dao.create(u)
    assert created, "Échec de création de l'utilisateur de test"
    assert u.id_utilisateur, "id_utilisateur non renseigné après création"
    return u
