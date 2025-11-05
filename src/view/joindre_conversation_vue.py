from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from src.service.conversation_service import ConversationService
from src.dao.personnage_ia_dao import PersonnageIADao
import traceback

class JoindreConversationVue(VueAbstraite):
    def __init__(self, message: str = ""):
        self.message = message
        self.service = ConversationService()

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        try:
            s = Session()
            if not s.utilisateur:
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Connecte-toi d'abord.")

            token = inquirer.text(message="Entrer le token de la conversation :").execute().strip().upper()
            if not token:
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Opération annulée.")

            conv = self.service.join_by_token(s.utilisateur["id_utilisateur"], token)
            if not conv:
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Token invalide ou conversation non collaborative.")

            # Session : ID conv + token + flag collab
            s.conversation_id = conv.id_conversation
            s.conversation_is_collab = bool(conv.is_collab)
            s.conversation_token = conv.token_collab

            # Charger le personnage de la conversation
            from src.dao.personnage_ia_dao import PersonnageIADao
            pdao = PersonnageIADao()
            perso = pdao.find_by_id(conv.id_personnageIA)
            if perso:
                s.personnage = {
                    "id_personnageIA": perso.id_personnageIA,
                    "name": perso.name,
                    "system_prompt": perso.system_prompt,
                }

            print(f"\nRejoint la conversation « {conv.titre or '(sans titre)'} ».")

            from view.reponse_ia_vue import ReponseIAVue
            return ReponseIAVue()

        except Exception as e:
            print("\n[JoindreConversationVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Erreur lors de la jonction (voir terminal).")
