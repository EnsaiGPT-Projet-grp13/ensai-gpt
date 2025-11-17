from unittest.mock import Mock
from service.stats_service import StatsService
def test_get_user_statistics_retourne_un_dict():
    fake_dao = Mock()
    fake_dao.nbre_msgs_utilisateur.return_value = 42
    fake_dao.nbre_conv_utilisateurs.return_value = 10
    fake_dao.moyenne_msg_par_conv.return_value = 4.2
    fake_dao.most_used_persona_for_user.return_value = "BotChef"

    service = StatsService()
    service.stats_dao = fake_dao  # <--- on injecte le mock

    stats = service.get_user_statistics(5)

    assert stats["total_messages"] == 42
    assert stats["total_conversations"] == 10
    assert stats["avg_messages_per_conversation"] == 4.2
    assert stats["most_used_persona"] == "BotChef"

def test_get_user_statistics_appelle_chaque_methode_dao():
    fake_dao = Mock()
    fake_dao.nbre_msgs_utilisateur.return_value = 0
    fake_dao.nbre_conv_utilisateurs.return_value = 0
    fake_dao.moyenne_msg_par_conv.return_value = 0
    fake_dao.most_used_persona_for_user.return_value = None

    service = StatsService()
    service.stats_dao = fake_dao

    service.get_user_statistics(10)

    fake_dao.nbre_msgs_utilisateur.assert_called_once_with(10)
    fake_dao.nbre_conv_utilisateurs.assert_called_once_with(10)
    fake_dao.moyenne_msg_par_conv.assert_called_once_with(10)
    fake_dao.most_used_persona_for_user.assert_called_once_with(10)
