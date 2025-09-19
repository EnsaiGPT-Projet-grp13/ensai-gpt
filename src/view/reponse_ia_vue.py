# src/view/reponse_ia_vue.py
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from utils.ia_client import IAClient
import traceback

class ReponseIAVue(VueAbstraite):
    def __init__(self, first_user_message: str | None = None, system_prompt: str | None = None) -> None:
        super().__init__(message="")  # <-- important
        self.client = IAClient(system_prompt or "Tu es un assistant utile.")
        self._first = (first_user_message or "").strip()

    # (optionnel) tu peux aussi surcharger afficher() si tu ne veux rien afficher :
    # def afficher(self): pass

    def choisir_menu(self):
        try:
            if self._first:
                answer = self.client.ask(self._first)
                print("\n--- Réponse de l'IA ---\n")
                print(answer)
                self._first = ""

            user_msg = inquirer.text(message="Ton message (Entrée pour quitter) :").execute()
            if not user_msg.strip():
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Chat terminé.")

            answer = self.client.ask(user_msg.strip())
            print("\n--- Réponse de l'IA ---\n")
            print(answer)
            return self

        except Exception as e:
            print("\n[ReponseIAVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Erreur dans le chat (voir terminal).")
