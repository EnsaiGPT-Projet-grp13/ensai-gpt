from tabulate import tabulate

from objects.session import Session
from service.stats_service import StatsService
from view.vue_abstraite import VueAbstraite


class StatistiquesVue(VueAbstraite):
    def __init__(self):
        s = Session()
        self.user_id = s.utilisateur.get("id_utilisateur")
        self.stats_service = StatsService()

    def afficher(self):
        # On récupère toutes les stats en une fois depuis le service
        stats = self.stats_service.get_user_statistics()

        total_messages = stats["total_messages"]
        total_conversations = stats["total_conversations"]
        moyenne_messages_par_conversation = stats["avg_messages_per_conversation"]
        persona_le_plus_utilise = stats["most_used_personas"]
        nb_personnages_IA_utilises = stats["nb_personnages_ia_utilises"]

        headers = ["Statistique", "Valeur"]
        rows = [
            ["Total Messages", total_messages or "Aucun message"],
            ["Total Conversations", total_conversations or "Aucune conversation"],
            [
                "Moyenne Messages par Conversation",
                (
                    f"{moyenne_messages_par_conversation:.2f}"
                    if moyenne_messages_par_conversation
                    else "Aucune donnée pour la moyenne"
                ),
            ],
            [
                "Persona le plus utilisé",
                (
                    ", ".join([p["name"] for p in persona_le_plus_utilise])
                    if persona_le_plus_utilise
                    else "Aucun persona utilisé"
                ),
            ],
            [
                "Nombre de Personnages IA utilisés",
                nb_personnages_IA_utilises or "Aucun personnage IA utilisé",
            ],
        ]

        print("\n--- Statistiques ---")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print("\n--------------------")

    def choisir_menu(self):
        from view.menu_utilisateur_vue import MenuUtilisateurVue

        return MenuUtilisateurVue()
