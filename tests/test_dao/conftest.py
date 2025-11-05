import pytest
import os
import pytest
from unittest.mock import patch
from unittest import mock

import sys

# Ajouter le répertoire src au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.utils.reset_database import ResetDatabase
from src.utils.securite import hash_pwd

from src.dao.utilisateur_dao import UtilisateurDao
from src.objects.utilisateur import Utilisateur
from src.dao.conversation_dao import ConversationDao
from src.objects.conversation import Conversation
from src.dao.personnage_ia_dao import PersonnageIADao
from src.objects.personnage_ia import PersonnageIA
from src.dao.message_dao import MessageDao
from src.objects.message import Message
#from src.dao.session_dao import SessionDao
#from src.objects.session import Session

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test (schéma de test + reset BDD)."""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        # Mock de la fonction de réinitialisation de la base de données pour éviter la réelle réinitialisation
        with mock.patch('src.utils.reset_database.ResetDatabase.lancer') as mock_lancer:
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
        mdp_hash=hash_pwd("mdpAlice", "alice@test.com"),
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
    assert created, "Échec de création de l'utilisateur de test"
    assert p.id_personnageIA, "id_conversation non renseigné après création"
    return p

@pytest.fixture
def conversation_existante(utilisateur_existant, personnageIA_existant):
    """Crée une conversation en BDD et la retourne (utilisé par plusieurs tests)."""
    c = Conversation(
        id_conversation=None,
        id_proprio=utilisateur_existant.id_utilisateur, 
        id_personnageIA=personnageIA_existant.id_personnageIA, 
        titre="test",
    )
    created = ConversationDao().create(c)
    assert created, "Échec de création de l'utilisateur de test"
    assert c.id_conversation, "id_conversation non renseigné après création"
    return c
