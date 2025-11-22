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
