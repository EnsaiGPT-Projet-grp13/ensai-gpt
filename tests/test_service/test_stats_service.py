# tests/test_service/test_stats_service.py

from unittest.mock import Mock
from service.stats_service import StatsService


def test_get_user_statistics_retourne_un_dict():
    fake_dao = Mock()
    fake_dao.nbre_msgs_utilisateur.return_value = 42
    fake_dao.nbre_conv_utilisateurs.return_value = 10
    fake_dao.moyenne_msg_par_conv.return_value = 4.2
    fake_dao.most_used_personas_for_user.return_value = ["BotChef", "BotDev"]
    fake_dao.nbre_personnages_IA_utilises.return_value = 2

    service = StatsService()
    service.stats_dao = fake_dao  # injection du mock

    stats = service.get_user_statistics()

    assert stats["total_messages"] == 42
    assert stats["total_conversations"] == 10
    assert stats["avg_messages_per_conversation"] == 4.2
    assert stats["most_used_personas"] == ["BotChef", "BotDev"]
    assert stats["nb_personnages_ia_utilises"] == 2


def test_get_user_statistics_appelle_chaque_methode_dao():
    fake_dao = Mock()
    fake_dao.nbre_msgs_utilisateur.return_value = 0
    fake_dao.nbre_conv_utilisateurs.return_value = 0
    fake_dao.moyenne_msg_par_conv.return_value = 0.0
    fake_dao.most_used_personas_for_user.return_value = []
    fake_dao.nbre_personnages_IA_utilises.return_value = 0

    service = StatsService()
    service.stats_dao = fake_dao

    service.get_user_statistics()

    fake_dao.nbre_msgs_utilisateur.assert_called_once_with()
    fake_dao.nbre_conv_utilisateurs.assert_called_once_with()
    fake_dao.moyenne_msg_par_conv.assert_called_once_with()
    fake_dao.most_used_personas_for_user.assert_called_once_with()
    fake_dao.nbre_personnages_IA_utilises.assert_called_once_with()
