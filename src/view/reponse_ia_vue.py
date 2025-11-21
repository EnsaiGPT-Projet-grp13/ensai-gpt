from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.conversation_service import ConversationService
import traceback


class ReponseIAVue(VueAbstraite):
    def __init__(self, first_user_message: str | None = None):
        super().__init__(message="")
        self._first = (first_user_message or "").strip()
        self.service = ConversationService()

    def _print_banner(self, s: Session):
        if s.conversation_is_collab and s.conversation_token:
            print("====================================")
            print("  Conversation COLLABORATIVE")
            print(f"  Token : {s.conversation_token}")
            print(
                "  Partagez ce token pour inviter d'autres utilisateurs à rejoindre cette conversation collaborative."
            )
            print("====================================\n")

    def choisir_menu(self):
        try:
            s = Session()
            self.service._ensure_conversation(s)

            # Garde-fous
            if not isinstance(s.utilisateur, dict) or not s.utilisateur.get("id_utilisateur"):
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Connecte-toi d'abord.")

            if not isinstance(s.personnage, dict) or not s.personnage.get("id_personnageIA"):
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Sélectionne un personnage d'abord.")

            if not s.conversation_id:
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Impossible de créer la conversation (voir logs).")

            self._print_banner(s)

            if self._first:
                ia_text, _ = self.service.send_user_and_get_ai(
                    cid=s.conversation_id,
                    id_user=int(s.utilisateur["id_utilisateur"]),
                    personnage=s.personnage,
                    user_text=self._first,
                )
                print("\n--- Réponse de l'IA ---\n")
                print(ia_text)
                print("\n-----------------------\n")
                self._first = ""
                self._print_banner(s)

            while True:
                pname = s.personnage.get("name", "Assistant")
                user_msg = (
                    inquirer.text(
                        message=f"[{pname}] Ton message (Entrée vide pour quitter) :"
                    ).execute()
                    or ""
                )

                if not user_msg.strip():
                    from view.menu_utilisateur_vue import MenuUtilisateurVue

                    return MenuUtilisateurVue("Conversation terminée.")

                ia_text, _ = self.service.send_user_and_get_ai(
                    cid=s.conversation_id,
                    id_user=int(s.utilisateur["id_utilisateur"]),
                    personnage=s.personnage,
                    user_text=user_msg.strip(),
                )
                print("\n--- Réponse de l'IA ---\n")
                print(ia_text)
                print("\n-----------------------\n")
                self._print_banner(s)

        except Exception as e:
            print("\n[ReponseIAVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.menu_utilisateur_vue import MenuUtilisateurVue

            return MenuUtilisateurVue("Erreur dans le chat (voir terminal).")
