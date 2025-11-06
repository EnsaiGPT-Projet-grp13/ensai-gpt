from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from objects.session import Session
from src.service.conversation_service import ConversationService
from src.service.message_service import MessageService



class RechercheConversationMotsVue(VueAbstraite):
    """Vue de recherche des conversations par des mots clés"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Insertion des mots recherchés"""
        print("\n" + "-" * 50 + "\nHistorique\n" + "-" * 50 + "\n")
        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        service = ConversationService()
        conversations = service.liste_resumee_accessible_pour_utilisateur(id_utilisateur)
        if not conversations:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Aucune conversation dans l'historique.")

        mots = inquirer.text(message="Quel mots clés recherchez vous dans vos anciennes conversations ? :").execute().strip().lower()
        listes_message = MessageService().recherche_mots_message(id_utilisateur, mots)
        if not listes_message:
            from view.historique_vue import HistoriqueVue
            return HistoriqueVue("Aucune conversation ne contient ces mots")

        choix = [f"{m.get('contenu')} par {m.get('expediteur')} (id_conversation#{m.get('id_conversation')})" for m in listes_message] + ["Retour"]
        label = inquirer.select(message="Quelle conversation voulez-vous ?", choices=choix).execute()
        if label == "Retour":
            # Retourne vers la vue du menue de l'utilisateur
            from view.historique_vue import HistoriqueVue
            return HistoriqueVue()
        if "#" in label and ")" in label:
            pid = int(label.split("#")[-1].rstrip(")"))
        else:
            raise ValueError("Format de label incorrect, impossible d'extraire l'ID.")
        conversation = next(c for c in conversations if c.get('id_conversation') == pid)
        id_conversation = conversation.get('id_conversation')

        conversation_choisie = service.get(id_conversation)
        s.conversation_id = id_conversation

        from view.parametre_conversation_vue import ParametreConversationVue
        return ParametreConversationVue()