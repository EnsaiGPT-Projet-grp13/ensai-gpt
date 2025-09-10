# src/view/reponseIA_vue.py
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from utils.ia_client import IAClient


class ReponseIAVue(VueAbstraite):
    """Vue terminal de chat, délègue l’appel IA à IAClient."""

    def __init__(self, first_user_message: str | None = None, system_prompt: str | None = None) -> None:
        self.client = IAClient(system_prompt or "Tu es un assistant utile.")
        self._first = (first_user_message or "").strip()

    def choisir_menu(self):
        try:
            # 1) première question éventuelle
            if self._first:
                answer = self.client.ask(self._first)
                print("\n--- Réponse de l'IA ---\n")
                print(answer)
                self._first = ""  # consommée

            # 2) boucle utilisateur
            user_msg = inquirer.text(message="Ton message (Entrée pour quitter) :").execute()
            if not user_msg.strip():
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Chat terminé.")

            answer = self.client.ask(user_msg.strip())
            print("\n--- Réponse de l'IA ---\n")
            print(answer)

            # 3) continuer le chat
            return self

        except Exception as e:
            print("\n[ReponseIAVue] Exception :", repr(e))
            import traceback; print(traceback.format_exc())
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Erreur dans le chat (voir terminal).")
