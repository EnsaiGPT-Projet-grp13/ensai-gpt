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

    def choisir_menu(self):
        # Initialisation de StatsDao pour interagir avec la base de données
        stats_dao = StatsDao()

        # Récupérer les statistiques
        total_messages = stats_dao.nbre_msgs_utilisateur()
        total_conversations = stats_dao.nbre_conv_utilisateurs()
        avg_messages_per_conversation = stats_dao.moyenne_msg_par_conv()
        most_used_persona = stats_dao.most_used_persona_for_user()

        # Créer un tableau avec les statistiques
        headers = ["Statistique", "Valeur"]  # En-têtes du tableau
        rows = [
            ["Total Messages", total_messages if total_messages else "Aucun message"],
            ["Total Conversations", total_conversations if total_conversations else "Aucune conversation"],
            ["Average Messages per Conversation", f"{avg_messages_per_conversation:.2f}" if avg_messages_per_conversation else "Aucune donnée pour la moyenne"],
            ["Most Used Persona", most_used_persona if most_used_persona else "Aucun persona utilisé"]
        ]

        # Affichage du tableau
        print("\n--- Statistiques ---")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        print("\n--------------------")

        # Retourner au menu utilisateur
        from view.menu_utilisateur_vue import MenuUtilisateurVue
        return MenuUtilisateurVue()


    def afficher(self):
        return self.choisir_menu()

