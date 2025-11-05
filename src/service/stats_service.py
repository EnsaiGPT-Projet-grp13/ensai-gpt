from src.dao.stats_dao import StatsDao

class StatsService:
    def __init__(self, db):
        self.db = db
        self.stats_dao = StatsDao(db)

    def get_user_statistics(self, user_id):
        total_messages = self.stats_dao.nbre_msgs_utilisateur(user_id)
        total_conversations = self.stats_dao.nbre_conv_utilisateurs(user_id)
        avg_messages_per_conversation = self.stats_dao.moyenne_msg_par_conv(user_id)
        most_used_persona = self.stats_dao.most_used_persona_for_user(user_id)

        stats = {
            "total_messages": total_messages,
            "total_conversations": total_conversations,
            "avg_messages_per_conversation": avg_messages_per_conversation,
            "most_used_persona": most_used_persona
        }

        return stats
