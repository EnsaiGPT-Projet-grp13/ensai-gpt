# tests/test_service/conftest.py
import pytest

from service.conversation_service import ConversationService


# === Objets factices communs pour les tests de services ===

class SessionFactice:
    def __init__(self):
        self.utilisateur = None
        self.personnage = None
        self.conversation_id = None
        self.conversation_is_collab = False
        self.conversation_token = None
        self.conversation_title = None


class UtilisateurFactice:
    def __init__(self, id_utilisateur, temperature=None, top_p=None, max_tokens=None):
        self.id_utilisateur = id_utilisateur
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens


class PersonnageFactice:
    def __init__(self, id_personnageIA, name, system_prompt):
        self.id_personnageIA = id_personnageIA
        self.name = name
        self.system_prompt = system_prompt


# === Fixtures réutilisables dans tous les tests de services ===

@pytest.fixture
def session_factice():
    """Session factice de base pour les tests de services."""
    return SessionFactice()


@pytest.fixture
def utilisateur_factice():
    """Utilisateur factice avec des préférences par défaut."""
    return UtilisateurFactice(
        id_utilisateur=5,
        temperature=0.9,
        top_p=0.8,
        max_tokens=200,
    )


@pytest.fixture
def personnage_factice():
    """Personnage IA factice."""
    return PersonnageFactice(
        id_personnageIA=3,
        name="BotTest",
        system_prompt="Prompt de test",
    )


@pytest.fixture
def service_conversation():
    """Instance de ConversationService pour les tests."""
    return ConversationService()
