from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session
from src.service.conversation_service import ConversationService
import traceback

class ReponseIAVue(VueAbstraite):
    def __init__(self, first_user_message: str | None = None):
        super().__init__(message="")
        self._first = (first_user_message or "").strip()
        self.service = ConversationService()

    def _ensure_conversation(self, s: Session):
        if s.personnage is None or not s.utilisateur:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Sélectionne un personnage et connecte-toi d'abord.")
        if not getattr(s, "conversation_id", None):
            conv = self.service.start(
                id_user=s.utilisateur["id_utilisateur"],
                personnage=s.personnage,
                titre=(s.conversation_title or f"Chat avec {s.personnage['name']}"),
                temperature=s.utilisateur.get("temperature", 0.7) if isinstance(s.utilisateur, dict) else 0.7,
                top_p=s.utilisateur.get("top_p", 1.0) if isinstance(s.utilisateur, dict) else 1.0,
                max_tokens=s.utilisateur.get("max_tokens", 150) if isinstance(s.utilisateur, dict) else 150,
            )
            s.conversation_id = conv.id_conversation
            s.conversation_title = None  # <--- reset après création
        return None

    def choisir_menu(self):
        try:
            s = Session()
            ret = self._ensure_conversation(s)
            if ret:
                return ret

            if self._first:
                ia_text, _ = self.service.send_user_and_get_ai(
                    cid=s.conversation_id,
                    id_user=s.utilisateur["id_utilisateur"],
                    personnage=s.personnage,
                    user_text=self._first,
                    temperature=s.utilisateur.get("temperature", 0.7) if isinstance(s.utilisateur, dict) else 0.7,
                    top_p=s.utilisateur.get("top_p", 1.0) if isinstance(s.utilisateur, dict) else 1.0,
                    max_tokens=s.utilisateur.get("max_tokens", 150) if isinstance(s.utilisateur, dict) else 150,
                )
                print("\n--- Réponse de l'IA ---\n")
                print(ia_text)
                print("\n-----------------------\n")
                self._first = ""

            while True:
                user_msg = inquirer.text(
                    message=f"[{s.personnage['name']}] Ton message (Entrée vide pour terminer) :"
                ).execute()
                if not user_msg.strip():
                    from view.menu_utilisateur_vue import MenuUtilisateurVue
                    return MenuUtilisateurVue("Conversation terminée.")

                ia_text, _ = self.service.send_user_and_get_ai(
                    cid=s.conversation_id,
                    id_user=s.utilisateur["id_utilisateur"],
                    personnage=s.personnage,
                    user_text=user_msg.strip(),
                    temperature=s.utilisateur.get("temperature", 0.7) if isinstance(s.utilisateur, dict) else 0.7,
                    top_p=s.utilisateur.get("top_p", 1.0) if isinstance(s.utilisateur, dict) else 1.0,
                    max_tokens=s.utilisateur.get("max_tokens", 150) if isinstance(s.utilisateur, dict) else 150,
                )
                print("\n--- Réponse de l'IA ---\n")
                print(ia_text)
                print("\n-----------------------\n")

        except Exception as e:
            print("\n[ReponseIAVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Erreur dans le chat (voir terminal).")
