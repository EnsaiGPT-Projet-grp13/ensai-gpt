from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from src.service.conversation_service import ConversationService



class RechercheConversationTitreVue(VueAbstraite):
    """Vue des options au sujet de l'historique de l'application"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Insertion du titre recherché"""
        print("\n" + "-" * 50 + "\nRecherhce conversation titre\n" + "-" * 50 + "\n")
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        service = ConversationService()
        conversations = service.liste_resumee_accessible_pour_utilisateur(id_utilisateur)
        if not conversations:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Aucune conversation dans l'historique.")
        titre = inquirer.text(message="Quel titre recherchez vous ? :").execute().strip().lower()
        listes_titres = 


        choix = [f"{c.get('titre')} avec {c.get('personnage_name')} (id_conversation#{c.get('id_conversation')})" for c in conversations] + ["Retour"]
        label = inquirer.select(message="Quelle conversation voulez-vous ?", choices=choix).execute()

