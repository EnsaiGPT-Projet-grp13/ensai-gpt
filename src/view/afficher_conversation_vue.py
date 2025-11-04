from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from src.service.conversation_service import ConversationService


class AfficherConversationVue(VueAbstraite):
    """Vue des dernière conversation (titre et persoIA uniquement et limiter à un nombre)"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Présentation de tous les titres et personnages IA des conversations"""
        print("\n" + "-" * 50 + "\nListe des dernières conversations\n" + "-" * 50 + "\n")

        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        service = ConversationService()
        conversations = service.liste_resumee_accessible_pour_utilisateur(id_utilisateur)
        print(conversations)
        if not conversations:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Aucune conversation dans l'historique.")

        choix = [f"{c.get('titre')} avec {c.get('personnage_name')}" for c in conversations]
        label = inquirer.select(message="Choisir une conversation précédente :", choices=choix).execute()
        pid = int(label.split("#")[-1].rstrip(")"))
        conversation = next(c for c in conversations if c.id_conversation == pid)

        id = conversation.get('id_conversation')



        
        
        #texte = inquirer.text(message=f"[{perso.name}] Première question ?").execute()
        from view.parametre_conversation_vue import ParametreConversationVue
        return ParametreConversationVue
