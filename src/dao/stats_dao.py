from src.dao.db import DBConnection
from collections import Counter
import os
from objects.session import Session  # Assurez-vous que la classe Session est bien importée

SCHEMA = os.getenv("POSTGRES_SCHEMA", "public")

class StatsDao:
    def __init__(self):
        self.conn = DBConnection().connection

    def nbre_msgs_utilisateur(self):
        """Retourne le nombre de messages envoyés par l'utilisateur connecté."""
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        print(f"ID de l'utilisateur connecté : {id_utilisateur}")  # Débogage
        query = f"""
        SELECT COUNT(*) AS count
        FROM {SCHEMA}.message
        WHERE expediteur = 'utilisateur' AND id_utilisateur = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (id_utilisateur,))
            result = cur.fetchone()

        # Débogage: Afficher le résultat brut
        print(f"Resultat nbre_msgs_utilisateur: {result}")

        if result is None:
            return 0

        return result['count']



    def nbre_conv_utilisateurs(self):
        """Retourne le nombre de conversations pour l'utilisateur connecté."""
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        query = f"""
        SELECT COUNT(*) 
        FROM {SCHEMA}.conversation
        WHERE id_proprio = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (id_utilisateur,))
            result = cur.fetchone()

        # Débogage: Afficher le résultat brut
        print(f"Resultat nbre_conv_utilisateurs: {result}")

        if result is None:
            return 0

        return result[0]

    def moyenne_msg_par_conv(self):
        """Retourne la moyenne de messages par conversation pour l'utilisateur connecté."""
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        query = f"""
        SELECT id_conversation, COUNT(*) as message_count
        FROM {SCHEMA}.message
        WHERE expediteur = 'utilisateur' AND id_utilisateur = %s
        GROUP BY id_conversation
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (id_utilisateur,))
            rows = cur.fetchall()

        # Débogage: Afficher les résultats bruts de la requête
        print(f"Resultat moyenne_msg_par_conv: {rows}")

        if len(rows) == 0:
            return 0

        total_messages = sum(row[1] for row in rows)  # row[1] est le compte des messages par conversation
        total_conversations = len(rows)

        return total_messages / total_conversations

    def most_used_persona_for_user(self):
        """Retourne le persona le plus utilisé par l'utilisateur connecté."""
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        query = f"""
        SELECT c.id_personnageIA, p.name
        FROM {SCHEMA}.conversation c
        JOIN {SCHEMA}.personnageIA p ON c.id_personnageIA = p.id_personnageIA
        WHERE c.id_proprio = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (id_utilisateur,))
            rows = cur.fetchall()

        # Débogage: Afficher les résultats bruts de la requête
        print(f"Resultat most_used_persona_for_user: {rows}")

        if len(rows) == 0:
            return None

        persona_ids = [row[0] for row in rows]  # row[0] est l'id_personnageIA
        persona_counts = Counter(persona_ids)

        most_common_persona = persona_counts.most_common(1)

        most_used_persona_id = most_common_persona[0][0]

        most_used_persona_name = None
        for row in rows:
            if row[0] == most_used_persona_id:
                most_used_persona_name = row[1]  # row[1] est le nom du persona
                break

        return most_used_persona_name
