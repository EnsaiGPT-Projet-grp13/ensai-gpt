from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from dao.stats_dao import StatsDao
from tabulate import tabulate  # Pour afficher le tableau
from objects.session import Session

class StatistiquesVue(VueAbstraite):
    def __init__(self):
        # On récupère l'utilisateur connecté depuis la session
        s = Session()
        self.user_id = s.utilisateur.get("id_utilisateur")  # Utilisation de la session pour récupérer l'ID de l'utilisateur

    def afficher(self):
        # Initialisation de StatsDao pour interagir avec la base de données
        stats_dao = StatsDao()

        # Récupérer les statistiques
        total_messages = stats_dao.nbre_msgs_utilisateur()
        total_conversations = stats_dao.nbre_conv_utilisateurs()
        moyenne_messages_par_conversation = stats_dao.moyenne_msg_par_conv()
        persona_le_plus_utlise = stats_dao.most_used_personas_for_user()
        nb_personnages_IA_utilises = stats_dao.nbre_personnages_IA_utilises()

        # Créer un tableau avec les statistiques
        headers = ["Statistique", "Valeur"]  # En-têtes du tableau
        rows = [
            ["Total Messages", total_messages if total_messages else "Aucun message"],
            ["Total Conversations", total_conversations if total_conversations else "Aucune conversation"],
            ["Moyenne Messages par Conversation", f"{moyenne_messages_par_conversation:.2f}" if moyenne_messages_par_conversation else "Aucune donnée pour la moyenne"],
            ["Persona le plus utilisé", ", ".join([persona["name"] for persona in persona_le_plus_utlise]) if persona_le_plus_utlise else "Aucun persona utilisé"],
            ["Nombre de Personnages IA utilisés", nb_personnages_IA_utilises if nb_personnages_IA_utilises else "Aucun personnage IA utilisé"]
        ]
        

        # Affichage du tableau
        print("\n--- Statistiques ---")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print("\n--------------------")

    def choisir_menu(self):
        from view.menu_utilisateur_vue import MenuUtilisateurVue
        return MenuUtilisateurVue()