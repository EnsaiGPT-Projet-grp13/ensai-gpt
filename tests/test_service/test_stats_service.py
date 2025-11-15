# tests/test_service/test_stats_service.py

import pytest
from unittest.mock import Mock

from service.stats_service import StatsService


@pytest.fixture
def stats_service(monkeypatch):
    """
    Service StatsService avec un StatsDao mocké.
    On monkeypatch StatsDao AVANT d'instancier StatsService,
    pour éviter l'appel au vrai constructeur.
    """
    fake_db = Mock()

    # Instance de DAO factice qui sera utilisée dans les tests
    fake_stats_dao = Mock()

    # Quand StatsService fera StatsDao(db), on veut qu'il reçoive fake_stats_dao.
    def fake_stats_dao_constructor(db):
        # On peut vérifier que db est bien reçu si on veut
        return fake_stats_dao

    # IMPORTANT : on monkeypatch la classe StatsDao dans le module service.stats_service
    monkeypatch.setattr(
        "service.stats_service.StatsDao",
        fake_stats_dao_constructor
    )

    service = StatsService(fake_db)
    # Par sécurité, on s'assure que l'attribut stats_dao référence bien notre mock
    service.stats_dao = fake_stats_dao
    return service


def test_get_user_statistics_retourne_un_dict(stats_service):
    """Le service doit retourner un dictionnaire avec les 4 clés attendues."""

    # On configure ce que le DAO mocké doit renvoyer
    stats_service.stats_dao.nbre_msgs_utilisateur.return_value = 42
    stats_service.stats_dao.nbre_conv_utilisateurs.return_value = 10
    stats_service.stats_dao.moyenne_msg_par_conv.return_value = 4.2
    stats_service.stats_dao.most_used_persona_for_user.return_value = "BotChef"

    stats = stats_service.get_user_statistics(5)

    assert isinstance(stats, dict)
    assert set(stats.keys()) == {
        "total_messages",
        "total_conversations",
        "avg_messages_per_conversation",
        "most_used_persona",
    }

    assert stats["total_messages"] == 42
    assert stats["total_conversations"] == 10
    assert stats["avg_messages_per_conversation"] == 4.2
    assert stats["most_used_persona"] == "BotChef"


def test_get_user_statistics_appelle_chaque_methode_dao(stats_service):
    """On vérifie que toutes les méthodes du DAO sont appelées exactement une fois."""

    stats_service.stats_dao.nbre_msgs_utilisateur.return_value = 0
    stats_service.stats_dao.nbre_conv_utilisateurs.return_value = 0
    stats_service.stats_dao.moyenne_msg_par_conv.return_value = 0
    stats_service.stats_dao.most_used_persona_for_user.return_value = None

    stats_service.get_user_statistics(10)

    stats_service.stats_dao.nbre_msgs_utilisateur.assert_called_once_with(10)
    stats_service.stats_dao.nbre_conv_utilisateurs.assert_called_once_with(10)
    stats_service.stats_dao.moyenne_msg_par_conv.assert_called_once_with(10)
    stats_service.stats_dao.most_used_persona_for_user.assert_called_once_with(10)
