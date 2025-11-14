import pytest
import os
import pytest
from unittest.mock import patch
from unittest import mock

import sys

# Ajouter le répertoire src au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.utilisateur_dao import UtilisateurDao
from objects.utilisateur import Utilisateur
from dao.conversation_dao import ConversationDao
from objects.conversation import Conversation
from dao.personnage_ia_dao import PersonnageIADao
from objects.personnage_ia import PersonnageIA
from dao.message_dao import MessageDao
from objects.message import Message
#from dao.session_dao import SessionDao
#from objects.session import Session

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test (schéma de test + reset BDD)."""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        # Mock de la fonction de réinitialisation de la base de données pour éviter la réelle réinitialisation
        with mock.patch('utils.reset_database.ResetDatabase.lancer') as mock_lancer:
            mock_lancer.return_value = True
            yield  # Setup complet, les tests peuvent commencer
        
@pytest.fixture
def utilisateur_existant():
    """Crée un utilisateur en BDD et le retourne (utilisé par plusieurs tests)."""
    mail = "alice@test.com"
    if UtilisateurDao().exists_mail(mail):
        utilisateur = UtilisateurDao().find_by_mail(mail)
        UtilisateurDao().delete(utilisateur.id_utilisateur)

    u = Utilisateur(
        prenom="Alice",
        nom="Test",
        mdp_hash=hash_password("mdpAlice", "alice@test.com"),
        naiss="2000-01-01",
        mail="alice@test.com",
    )
    created = UtilisateurDao().create(u)
    assert created, "Échec de création de l'utilisateur de test"
    assert u.id_utilisateur, "id_utilisateur non renseigné après création"
    return u

@pytest.fixture
def personnageIA_existant(utilisateur_existant):
    """Crée un personnageIA en BDD et le retourne (utilisé par plusieurs tests)."""
    p = PersonnageIA(
        id_personnageIA=None,
        name="Testeur",
        system_prompt="Neutre",
        created_by=utilisateur_existant.id_utilisateur,
    )
    created = PersonnageIADao().create(p)
    assert created, "Échec de création du personnage"
    return created


@pytest.fixture
def conversation_existante(utilisateur_existant, personnageIA_existant):
    """Crée une conversation en BDD et la retourne (utilisé par plusieurs tests)."""
    c = Conversation(
        id_conversation=None,
        id_proprio=utilisateur_existant.id_utilisateur, 
        id_personnageIA=personnageIA_existant.id_personnageIA, 
        titre="test",
        max_tokens=1000,
    )
    created = ConversationDao().create(c)
    assert created, "Échec de création de l'utilisateur de test"
    return c

@pytest.fixture
def session():
    pass

@pytest.fixture
def message():
    pass

