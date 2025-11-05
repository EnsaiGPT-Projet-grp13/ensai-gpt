from src.service.utilisateur_service import UtilisateurService  # Import de la classe UtilisateurService
from collections import Counter
import os
from dao.db import DBConnection
from objects.session import Session

SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")

class StatsDao:
    def __init__(self):
        self.conn = DBConnection().connection

    def nbre_msgs_utilisateur(self):
        """Retourne le nombre de messages envoyés par l'utilisateur connecté."""
        s = Session()
        user_id = s.utilisateur.get("id_utilisateur")
        user = UtilisateurService.trouver_par_id(user_id)  # Appel direct de la méthode de classe
        if not user:
            return 0  # Si l'utilisateur n'existe pas dans la DB

        query = f"""
        SELECT COUNT(*) AS count
        FROM {SCHEMA}.message
        WHERE expediteur = 'utilisateur' AND id_utilisateur = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (user.id_utilisateur,))
            result = cur.fetchone()
        
        if result is None:
            return 0
        return result['count']

    def nbre_conv_utilisateurs(self):
        """Retourne le nombre de conversations pour l'utilisateur connecté."""
        s = Session()
        user_id = s.utilisateur.get("id_utilisateur")
        user = UtilisateurService.trouver_par_id(user_id)  # Appel direct de la méthode de classe
        if not user:
            return 0  # Si l'utilisateur n'existe pas dans la DB

        query = f"""
        SELECT COUNT(*) AS count
        FROM {SCHEMA}.conversation
        WHERE id_proprio = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (user.id_utilisateur,))
            result = cur.fetchone()

        if result is None:
            return 0
        return result['count']

    def moyenne_msg_par_conv(self):
        """Retourne la moyenne de messages par conversation pour l'utilisateur connecté."""
        s = Session()
        user_id = s.utilisateur.get("id_utilisateur")
        user = UtilisateurService.trouver_par_id(user_id)  # Appel direct de la méthode de classe
        if not user:
            return 0  # Si l'utilisateur n'existe pas dans la DB

        query = f"""
        SELECT id_conversation, COUNT(*) as message_count
        FROM {SCHEMA}.message
        WHERE expediteur = 'utilisateur' AND id_utilisateur = %s
        GROUP BY id_conversation
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (user.id_utilisateur,))
            rows = cur.fetchall()
        
        if len(rows) == 0:
            return 0

        total_messages = sum(row['message_count'] for row in rows)
        total_conversations = len(rows)

        return total_messages / total_conversations

    def most_used_persona_for_user(self):
        """Retourne le persona le plus utilisé par l'utilisateur connecté."""
        s = Session()
        user_id = s.utilisateur.get("id_utilisateur")
        user = UtilisateurService.trouver_par_id(user_id)  # Appel direct de la méthode de classe
        if not user:
            return None  # Si l'utilisateur n'existe pas dans la DB

        query = f"""
        SELECT c.id_personnageIA, p.name
        FROM {SCHEMA}.conversation c
        JOIN {SCHEMA}.personnageIA p ON c.id_personnageIA = p.id_personnageIA
        WHERE c.id_proprio = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (user.id_utilisateur,))
            rows = cur.fetchall()

        if len(rows) == 0:
            return None

        persona_ids = [row['id_personnageIA'] for row in rows]
        persona_counts = Counter(persona_ids)

        most_common_persona = persona_counts.most_common(1)

        most_used_persona_id = most_common_persona[0][0]

        most_used_persona_name = None
        for row in rows:
            if row['id_personnageIA'] == most_used_persona_id:
                most_used_persona_name = row['name']
                break

        return most_used_persona_name
