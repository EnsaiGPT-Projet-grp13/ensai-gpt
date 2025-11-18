from typing import Any, Dict
from dao.stats_dao import StatsDao

class StatsService:
    """Service métier pour regrouper les statistiques utilisateur."""

    def __init__(self) -> None:
        self.stats_dao = StatsDao()

    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Récupère les stats pour l'utilisateur connecté
        (l'utilisateur est déterminé par la Session utilisée dans StatsDao).
        """
        total_messages = self.stats_dao.nbre_msgs_utilisateur()
        total_conversations = self.stats_dao.nbre_conv_utilisateurs()
        avg_messages_per_conversation = self.stats_dao.moyenne_msg_par_conv()
        most_used_personas = self.stats_dao.most_used_personas_for_user()
        nb_personnages_ia = self.stats_dao.nbre_personnages_IA_utilises()

        return {
            "total_messages": total_messages,
            "total_conversations": total_conversations,
            "avg_messages_per_conversation": avg_messages_per_conversation,
            "most_used_personas": most_used_personas,
            "nb_personnages_ia_utilises": nb_personnages_ia,
        }
