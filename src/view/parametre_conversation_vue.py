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
        if s.conversation_id is None:
            from view.historique_vue import HistoriqueVue
            return HistoriqueVue("Aucune conversation sélectionnée.")
        id_conversation = s.conversation_id
        conversation = ConversationService().get(id_conversation)
        print(f"Vous avez sélectionné la conversation : {conversation.titre}" )
        titre = conversation.titre

        choix = inquirer.select(
            message="Que voulez vous faire avec cette conversation ?",
            choices=[
                "Reprendre la conversation",
                "Afficher l'entièreté de la conversation",
                "Télécharger la conversation",
                "Supprimer la conversation",
                "Changer le titre",
                "Retour",
            ],
        ).execute()

        match choix:
            case "Reprendre la conversation":
                # Reprise de la conversation là où elle a été arrêtée
                id_personnage = conversation.id_personnageIA
                if personnage is not None:
                    s.personnage = asdict(personnage)
                    from view.reponse_ia_vue import ReponseIAVue
                    return ReponseIAVue()
                else:
                    print(f"Erreur : Le personnage avec l'ID {id_personnage} n'existe pas ou plus.")
                    from view.menu_utilisateur_vue import MenuUtilisateurVue
                    return MenuUtilisateurVue("Personnage non trouvé")

            case "Afficher l'entièreté de la conversation":
                # Retroune l'entièreté des échanges entre l'utilisateur et le LLM dans le cadre de la conversation choisie
                pass
                """from view.parametre_conversation_vue import ParametreConversationVue
                return ParametreConversationVue"""

            case "Changer le titre":
                # Modification du titre de la conversation sélectionnée
                nouveau_titre = inquirer.text(message="Comment voulez vous renommer votre conversation ? :").execute()
                ConversationService().modifier(conversation, nouveau_titre)
                from view.parametre_conversation_vue import ParametreConversationVue
                return ParametreConversationVue(f"Vous avez modifier {titre} par {nouveau_titre}")
            
            case "Télécharger la conversation":
                # Télécharge l'entièreté des échanges de la conversation choisie
                pass
                '''from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue()'''

            case "Supprimer la conversation":
                # Suppression de la conversation sélectionnée
                ConversationService().supprimer(conversation)
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue(f"Vous avez supprimé la conversation {titre}")

            case "Retour":
                # Retourne vers la vue du menue de l'utilisateur
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue()
