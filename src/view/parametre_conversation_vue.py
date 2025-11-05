from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite

class ParametreConversationVue(VueAbstraite):
    """Vue des options la conversation choisie"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Choix du menu suivant"""
        print("\n" + "-" * 50 + "\nOptions la conversation\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Que voulez vous faire avec cette conversation ?",
            choices=[
                "Reprendre la conversation",
                "Afficher l'entièreté de la conversation",
                "Télécharger la conversation",
                "Supperimer la converasation",
                "Changer le titre",
                "Quitter",
            ],
        ).execute()

        match choix:
            case "Reprendre la conversation":
                # Reprise de la conversation là où elle a été arrêtée
                pass
                """from view.afficher_conversation_vue import AfficherConversationVue
                return AfficherConversationVue()"""

            case "Afficher l'entièreté de la conversation":
                # Retroune l'entièreté des échanges entre l'utilisateur et le LLM dans le cadre de la conversation choisie
                pass
                """from view.parametre_conversation_vue import ParametreConversationVue
                return ParametreConversationVue"""

            case "Changer le titre":
                # Modification du titre de la conversation sélectionnée
                pass
                """from view.parametre_conversation_vue import ParametreConversationVue
                return ParametreConversationVue"""
            
            case "Télécharger la conversation":
                # Télécharge l'entièreté des échanges de la conversation choisie
                pass
                '''from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue()'''

            case "Suprimer la conversation":
                # Suppression de la conversation sélectionnée
                pass
                '''from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue()'''

            case "Quitter":
                # Retourne vers la vue du menue de l'utilisateur
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue()
