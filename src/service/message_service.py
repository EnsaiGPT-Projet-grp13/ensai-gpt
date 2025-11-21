from __future__ import annotations
from dao.message_dao import MessageDao


class MessageService:
    """
    Gère l'historique local du chat et l'appel à l'IA.
    """

    def __init__(self, system_prompt: str = "Tu es un assistant utile.") -> None:
        self.history: list[dict] = [{"role": "system", "content": system_prompt}]
        self.message_dao = MessageDao()

    def recherche_mots_message(self, id_utilisateur: int, mots: str, limite: int = 5):
        """Renvoie la liste des messages dans lesquels mots est présent"""
        return self.message_dao.recherche_mots_message(
            id_utilisateur, mots, limite=limite
        )

    def affichage_message_conversation(self, id_conversation: int):
        dao = MessageDao()
        messages = dao.list_for_conversation(id_conversation)

        if not messages:
            return "Aucun message trouvé pour cette conversation."

        lignes = []
        for msg in messages:
            lignes.append(f"Message de {msg.expediteur} : {msg.contenu}")

        return "\n".join(lignes)
