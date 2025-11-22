from __future__ import annotations
from dao.message_dao import MessageDao


class MessageService:
    """
    Gère l'historique local du chat et l'accès aux messages stockés en base.
    """

    def __init__(self, system_prompt: str = "Tu es un assistant utile.") -> None:
        self.history: list[dict] = [{"role": "system", "content": system_prompt}]
        self.message_dao = MessageDao()

    def recherche_mots_message(self, id_utilisateur: int, mots: str, limite: int = 5):
        """Renvoie la liste des messages dans lesquels `mots` est présent."""
        return self.message_dao.recherche_mots_message(
            id_utilisateur, mots, limite=limite
        )

    def affichage_message_conversation(self, id_conversation: int) -> str:
        """
        Affiche tous les messages d'une conversation en indiquant :
        - pour l'utilisateur : prénom + nom
        - pour l'IA : nom du personnage IA
        """
        from dao.utilisateur_dao import UtilisateurDao
        from dao.conversation_dao import ConversationDao
        from dao.personnage_ia_dao import PersonnageIADao

        messages = self.message_dao.list_for_conversation(id_conversation)

        if not messages:
            return "Aucun message trouvé pour cette conversation."

        conv = ConversationDao().find_by_id(id_conversation)
        perso_name = "IA"
        if conv and getattr(conv, "id_personnageIA", None):
            perso = PersonnageIADao().find_by_id(conv.id_personnageIA)
            if perso:
                perso_name = perso.name

        user_dao = UtilisateurDao()
        cache_users: dict[int, object] = {}

        lignes: list[str] = []
        for msg in messages:
            if msg.expediteur == "IA":
                auteur = f"{perso_name} (IA)"
            else:
                nom_complet = "Utilisateur inconnu"
                if msg.id_utilisateur is not None:
                    u = cache_users.get(msg.id_utilisateur)
                    if u is None:
                        u = user_dao.find_by_id(msg.id_utilisateur)
                        cache_users[msg.id_utilisateur] = u
                    if u:
                        nom_complet = f"{u.prenom} {u.nom}"
                auteur = nom_complet

            lignes.append(f"{auteur} : {msg.contenu}")

        return "\n\n".join(lignes)