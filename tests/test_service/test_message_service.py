import service.message_service as message_service
from service.message_service import MessageService
from objects.message import Message
import pytest


@pytest.fixture(autouse=True)
def restore_message_dao():
    original = message_service.MessageDao
    yield
    message_service.MessageDao = original


def test_message_service_init_default_prompt():
    service = MessageService()
    assert service.history[0]["content"] == "Tu es un assistant utile."


def test_message_service_init_custom_prompt():
    service = MessageService(system_prompt="Test prompt")
    assert service.history[0]["content"] == "Test prompt"


def test_recherche_mots_message_appelle_bons_arguments():
    class FakeDao:
        def __init__(self):
            self.last = None

        def recherche_mots_message(self, id_user, mots, limite=5):
            self.last = (id_user, mots, limite)
            return ["ok"]

    service = MessageService()
    fake = FakeDao()
    service.message_dao = fake

    res = service.recherche_mots_message(10, "abc", 7)
    assert res == ["ok"]
    assert fake.last == (10, "abc", 7)


def test_affichage_message_aucun_message():
    class FakeDao:
        def list_for_conversation(self, id_conv):
            assert id_conv == 123
            return []

    message_service.MessageDao = FakeDao

    service = MessageService()
    result = service.affichage_message_conversation(123)

    assert result == "Aucun message trouvé pour cette conversation."

def test_affichage_message_messages():
    # Messages factices
    msgs = [
        Message(
            id_message=1,
            id_conversation=1,
            expediteur="utilisateur",
            id_utilisateur=1,
            contenu="Hello",
        ),
        Message(
            id_message=2,
            id_conversation=1,
            expediteur="IA",
            id_utilisateur=None,
            contenu="Salut !",
        ),
    ]

    class FakeDao:
        def list_for_conversation(self, id_conv):
            assert id_conv == 1
            return msgs

    service = MessageService()
    service.message_dao = FakeDao()

    result = service.affichage_message_conversation(1)

    assert "Message de utilisateur : Hello" in result
    assert "Message de IA : Salut !" in result