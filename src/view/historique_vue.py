from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite


class HistoriqueVue(VueAbstraite):
    """Vue des options au sujet de l'historique de l'application"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Choix du menu suivant"""
        print("\n" + "-" * 50 + "\nHistorique\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Que voulez vous faire dans l'historique ?",
            choices=[
                "Afficher toutes les conversations",
                "Rechercher une conversation (par titre)",
                "Rechercher une conversation (par mots clés)",
                "Retour",
            ],
        ).execute()

        match choix:
            case "Afficher toutes les conversations":
                from view.afficher_conversation_vue import AfficherConversationVue
                return AfficherConversationVue()

            case "Rechercher une conversation (par titre)":
                from view.recherche_conversation_titre_vue import RechercheConversationTitreVue
                return RechercheConversationTitreVue()

            case "Rechercher une conversation (par mots clés)":
                from view.recherche_conversation_mots_vue import RechercheConversationMotsVue
                return RechercheConversationMotsVue()

            case "Retour":
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue()
