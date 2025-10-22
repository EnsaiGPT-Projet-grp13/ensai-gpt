from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session
from utils.ia_client import IAClient
import traceback


class ReponseIAVue(VueAbstraite):
    """
    Chat multi-tours basé sur IAClient.
    - Récupère le system_prompt depuis Session().personnage si présent
    - Envoie un premier message si fourni
    - Boucle: envoyer message / changer de personnage / retour menu
    """

    def __init__(self, first_user_message: str | None = None, system_prompt: str | None = None) -> None:
        super().__init__(message="")
        s = Session()
        perso = s.personnage or {}
        # priorité au paramètre explicite, sinon prompt du personnage, sinon défaut
        prompt = (system_prompt or perso.get("system_prompt") or "Tu es un assistant utile.").strip()

        self.client = IAClient(prompt)
        self._first = (first_user_message or "").strip()

        # (optionnel) tu peux vouloir afficher le nom du personnage en tête
        self._perso_name = perso.get("name", "Assistant")

    # def afficher(self): pass  # si tu ne veux rien afficher avant le chat

    def _ask_and_print(self, user_msg: str) -> None:
        """Envoie user_msg à l'IA et affiche la réponse proprement."""
        answer = self.client.ask(user_msg)
        print("\n--- Réponse de l'IA ---\n")
        print(answer)
        print("\n-----------------------\n")

    def choisir_menu(self):
        try:
            # 1) premier tour automatique si un message initial est fourni
            if self._first:
                self._ask_and_print(self._first)
                self._first = ""

            # 2) boucle chat
            while True:
                choix = inquirer.select(
                    message="Action :",
                    choices=[
                        "Envoyer un message",
                        "Changer de personnage",
                        "Retour au menu",
                    ],
                ).execute()

                if choix == "Retour au menu":
                    from view.menu_utilisateur_vue import MenuUtilisateurVue
                    return MenuUtilisateurVue("Chat terminé.")

                if choix == "Changer de personnage":
                    from view.choisir_personnage_vue import ChoisirPersonnageVue
                    return ChoisirPersonnageVue("Change un personnage, puis pose ta question.")

                # Envoyer un message
                user_msg = inquirer.text(message=f"[{self._perso_name}] Ton message (Entrée vide pour quitter) :").execute()
                if not user_msg.strip():
                    from view.menu_utilisateur_vue import MenuUtilisateurVue
                    return MenuUtilisateurVue("Chat terminé.")

                self._ask_and_print(user_msg.strip())

        except Exception as e:
            print("\n[ReponseIAVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Erreur dans le chat (voir terminal).")
