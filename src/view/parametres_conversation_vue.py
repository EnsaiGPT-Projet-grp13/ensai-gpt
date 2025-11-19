from InquirerPy import inquirer
from dataclasses import asdict
import urllib.parse
import os

from objects.session import Session
from service.message_service import MessageService
from service.personnage_service import PersonnageService
from service.conversation_service import ConversationService
from service.export_service import start_flask_server
from view.vue_abstraite import VueAbstraite

class ParametresConversationVue(VueAbstraite):
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
                personnage = PersonnageService().get_by_id(id_personnage)
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
                print("\n" + "-" * 50 + f"\n Conversation : {conversation.titre}\n" + "-" * 50 + "\n")
                MessageService().affichage_message_conversation(id_conversation)
                from view.parametre_conversation_vue import ParametresConversationVue
                return ParametresConversationVue()

            case "Changer le titre":
                # Modification du titre de la conversation sélectionnée
                nouveau_titre = inquirer.text(message="Comment voulez vous renommer votre conversation ? :").execute()
                ConversationService().modifier(conversation, nouveau_titre)
                from view.parametre_conversation_vue import ParametresConversationVue
                return ParametresConversationVue(f"Vous avez modifier {titre} par {nouveau_titre}")
            
            case "Télécharger la conversation":
                start_flask_server()
                nom_fichier = inquirer.text(message="Comment voulez-vous nommer votre fichier ? :").execute()
                titre_fichier = conversation.titre

                titre_fichier_encoded = urllib.parse.quote(titre_fichier)
                nom_fichier_encoded = urllib.parse.quote(nom_fichier)

                base_url = "http://127.0.0.1:5000"
                url_telechargement = f"{base_url}/telecharger/{id_conversation}?titre={titre_fichier_encoded}&fichier={nom_fichier_encoded}"

                import requests
                r = requests.get(url_telechargement)

                dossier_exports = "exports"
                os.makedirs(dossier_exports, exist_ok=True)
                chemin_fichier = os.path.join(dossier_exports, f"{nom_fichier}.txt")

                if r.status_code == 200:
                    with open(chemin_fichier, "wb") as f:
                        f.write(r.content)
                    message = f"Votre fichier a été téléchargé : {chemin_fichier}"
                else:
                    message = f"Erreur {r.status_code} : {r.text[:200]}"

                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue(message)

            case "Supprimer la conversation":
                # Suppression de la conversation sélectionnée
                ConversationService().supprimer(conversation)
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue(f"Vous avez supprimé la conversation {titre}")

            case "Retour":
                # Retourne vers la vue du menue de l'utilisateur
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue()
