from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from service.stats_service import StatsService
from tabulate import tabulate  
from objects.session import Session

class StatistiquesVue(VueAbstraite):
    def __init__(self):
        s = Session()
        self.user_id = s.utilisateur.get("id_utilisateur")  
        self.stats_service = StatsService()

    def afficher(self):
        stats = self.stats_service.get_user_statistics()

        
        total_messages = stats_dao.nbre_msgs_utilisateur()
        total_conversations = stats_dao.nbre_conv_utilisateurs()
        moyenne_messages_par_conversation = stats_dao.moyenne_msg_par_conv()
        persona_le_plus_utlise = stats_dao.most_used_personas_for_user()
        nb_personnages_IA_utilises = stats_dao.nbre_personnages_IA_utilises()

        
        headers = ["Statistique", "Valeur"] 
        rows = [
            ["Total Messages", total_messages if total_messages else "Aucun message"],
            ["Total Conversations", total_conversations if total_conversations else "Aucune conversation"],
            ["Moyenne Messages par Conversation", f"{moyenne_messages_par_conversation:.2f}" if moyenne_messages_par_conversation else "Aucune donnée pour la moyenne"],
            ["Persona le plus utilisé", ", ".join([persona["name"] for persona in persona_le_plus_utlise]) if persona_le_plus_utlise else "Aucun persona utilisé"],
            ["Nombre de Personnages IA utilisés", nb_personnages_IA_utilises if nb_personnages_IA_utilises else "Aucun personnage IA utilisé"]
        ]
        

        print("\n--- Statistiques ---")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print("\n--------------------")

    def choisir_menu(self):
        from view.menu_utilisateur_vue import MenuUtilisateurVue
        return MenuUtilisateurVue()