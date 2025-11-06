from InquirerPy import inquirer
from dataclasses import asdict

from objects.session import Session
from objects.personnage_ia import PersonnageIA
from src.service.personnage_service import PersonnageService
from src.service.conversation_service import ConversationService
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

        s = Session()
        if s.conversation is None:
            from view.historique_vue import HistoriqueVue
            return HistoriqueVue("Aucune conversation sélectionnée.")
        id_conversation = s.conversation.id_conversation
        conversation = ConversationService().get(id_conversation)

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
                id_personnage = conversation.id_personnageIA
                s.personnage = asdict(PersonnageService().get_by_id(id_personnage))
                from view.reponse_ia_vue import ReponseIAVue
                return ReponseIAVue()

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
