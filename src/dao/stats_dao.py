from dao.db import DBConnection
from src.service.utilisateur_service import UtilisateurService  # Import de la classe UtilisateurService
from collections import Counter
import os
from objects.session import Session

SCHEMA = os.getenv("POSTGRES_SCHEMA", "projetGPT")

class StatsDao:
    def __init__(self):
        self.conn = DBConnection().connection

    def nbre_msgs_utilisateur(self):
        """Retourne le nombre de messages envoyés par l'utilisateur connecté."""
        s = Session()
        user_id = s.utilisateur.get("id_utilisateur")  # Récupère l'ID de l'utilisateur depuis la session
        utilisateur_service = UtilisateurService()
        user = utilisateur_service.trouver_par_id(user_id)   # Appel de la méthode avec le bon paramètre
        if not user:
            return 0  # Si l'utilisateur n'existe pas, renvoie 0

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
        user_id = s.utilisateur.get("id_utilisateur")  # Récupère l'ID de l'utilisateur depuis la session
        utilisateur_service = UtilisateurService()
        user = utilisateur_service.trouver_par_id(user_id)
        if not user:
            return 0  # Si l'utilisateur n'existe pas, renvoie 0

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
        user_id = s.utilisateur.get("id_utilisateur")  # Récupère l'ID de l'utilisateur depuis la session
        utilisateur_service = UtilisateurService()
        user = utilisateur_service.trouver_par_id(user_id) 
        if not user:
            return 0  # Si l'utilisateur n'existe pas, renvoie 0

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

  
    def most_used_personas_for_user(self):
        s = Session()
        user_id = s.utilisateur.get("id_utilisateur")
        
        query = f"""
            SELECT c.id_personnageIA, p.name, COUNT(c.id_personnageIA) AS count
            FROM {SCHEMA}.conversation c
            JOIN {SCHEMA}.personnageIA p ON c.id_personnageIA = p.id_personnageIA
            WHERE c.id_proprio = %s
            GROUP BY c.id_personnageIA, p.name
            HAVING COUNT(c.id_personnageIA) = (
                SELECT MAX(count)
                FROM (
                    SELECT COUNT(c.id_personnageIA) AS count
                    FROM {SCHEMA}.conversation c
                    WHERE c.id_proprio = %s
                    GROUP BY c.id_personnageIA
                ) AS subquery
            )
            ORDER BY count DESC
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query, (user_id, user_id))
            rows = cur.fetchall()
        
        # Traiter les résultats de la requête
        most_used_personas = []
        for row in rows:
            most_used_personas.append({
                "id_personnageia": row["id_personnageia"],
                "name": row["name"],
                "count": row["count"]
            })
        
        return most_used_personas



    def nbre_personnages_IA_utilises(self):
        s = Session()
        user_id = s.utilisateur.get("id_utilisateur")  
        utilisateur_service = UtilisateurService()
        user = utilisateur_service.trouver_par_id(user_id)
        if not user:
            return 0  
        query = f"""
        SELECT COUNT(DISTINCT c.id_personnageIA) AS count
        FROM {SCHEMA}.conversation c
        WHERE c.id_proprio = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (user.id_utilisateur,))
            result = cur.fetchone()

        if result is None:
            return 0
        return result['count']
