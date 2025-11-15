# tests/test_service/test_message_service.py
import pytest
from unittest.mock import Mock

from service.message_service import MessageService
from objects.message import Message


# =========================
# Tests de __init__
# =========================

def test_message_service_init_utilise_prompt_par_defaut():
    service = MessageService()
    assert isinstance(service.history, list)
    assert len(service.history) == 1
    assert service.history[0]["role"] == "system"
    assert service.history[0]["content"] == "Tu es un assistant utile."


def test_message_service_init_utilise_prompt_personnalise():
    service = MessageService(system_prompt="Tu es un bot de test.")
    assert len(service.history) == 1
    assert service.history[0]["content"] == "Tu es un bot de test."


# =========================
# Tests de recherche_mots_message
# =========================

def test_recherche_mots_message_appelle_dao_avec_bons_arguments(monkeypatch):
    # On capture les arguments passés au DAO
    appels = {}

    class FauxMessageDao:
        def recherche_mots_message(self, id_utilisateur, mots, limite=5):
            appels["id_utilisateur"] = id_utilisateur
            appels["mots"] = mots
            appels["limite"] = limite
            return ["resultat1", "resultat2"]

    # Quand MessageService fait MessageDao(), il obtiendra notre faux DAO
    monkeypatch.setattr("service.message_service.MessageDao", FauxMessageDao)

    service = MessageService()
    res = service.recherche_mots_message(id_utilisateur=42, mots="test", limite=10)

    assert res == ["resultat1", "resultat2"]
    assert appels["id_utilisateur"] == 42
    assert appels["mots"] == "test"
    assert appels["limite"] == 10


# =========================
# Tests de affichage_message_conversartion
# =========================

def test_affichage_message_conversation_aucun_message(monkeypatch, capsys):
    class FauxMessageDao:
        def list_for_conversation(self, id_conversation: int):
            assert id_conversation == 123
            return []

    # Ici la méthode utilise directement MessageDao(), pas self.message_dao
    monkeypatch.setattr("service.message_service.MessageDao", FauxMessageDao)

    service = MessageService()
    service.affichage_message_conversartion(123)

    captured = capsys.readouterr()
    assert "Aucun message trouvé pour cette conversation." in captured.out


def test_affichage_message_conversation_affiche_tous_les_messages(monkeypatch, capsys):
    messages = [
        Message(
            id_message=1,
            id_conversation=1,
            expediteur="utilisateur",
            id_utilisateur=5,
            contenu="Bonjour",
        ),
        Message(
            id_message=2,
            id_conversation=1,
            expediteur="IA",
            id_utilisateur=None,
            contenu="Salut, comment puis-je aider ?",
        ),
    ]

    class FauxMessageDao:
        def list_for_conversation(self, id_conversation: int):
            assert id_conversation == 1
            return messages

    monkeypatch.setattr("service.message_service.MessageDao", FauxMessageDao)

    service = MessageService()
    service.affichage_message_conversartion(1)

    captured = capsys.readouterr()
    out = captured.out

    # On vérifie qu'on imprime bien les deux auteurs et leur contenu
    assert "Message de utilisateur" in out
    assert "Bonjour" in out
    assert "Message de IA" in out
    assert "Salut, comment puis-je aider ?" in out
