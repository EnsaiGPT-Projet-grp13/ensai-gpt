from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.conversation_service import ConversationService
import traceback


class JoindreConversationVue(VueAbstraite):
    def __init__(self, message: str = ""):
        self.message = message
        self.service = ConversationService()

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        from view.menu_utilisateur_vue import MenuUtilisateurVue
        from view.reponse_ia_vue import ReponseIAVue

        try:
            s = Session()
            if not s.utilisateur:
                return MenuUtilisateurVue("Connecte-toi d'abord.")

            user_id = s.utilisateur.get("id_utilisateur")
            if not user_id:
                return MenuUtilisateurVue("Utilisateur invalide en session.")

            # Boucle de saisie du token (pour permettre de réessayer)
            while True:
                token = inquirer.text(
                    message="Entrer le token de la conversation (Entrée vide pour annuler) :"
                ).execute()

                token = (token or "").strip().upper()

                # Annulation
                if not token:
                    return MenuUtilisateurVue("Opération annulée.")

                # On tente de rejoindre la conversation via le SERVICE
                conv = self.service.join_by_token(user_id, token)
                if not conv:
                    print(
                        "Token invalide ou conversation non collaborative. Réessaie.\n"
                    )
                    continue  # on redemande un token

                # Conversation OK : mise à jour de la session
                s.conversation_id = conv.id_conversation
                s.conversation_is_collab = bool(conv.is_collab)
                s.conversation_token = conv.token_collab

                # Récupérer le personnage via le SERVICE (plus de DAO ici)
                perso_dict = self.service.get_personnage_for_conversation(conv)
                if perso_dict:
                    s.personnage = perso_dict

                print(f"\nRejoint la conversation « {conv.titre or '(sans titre)'} ».")

                return ReponseIAVue()

        except Exception as e:
            print("\n[JoindreConversationVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur lors de la jonction (voir terminal).")
