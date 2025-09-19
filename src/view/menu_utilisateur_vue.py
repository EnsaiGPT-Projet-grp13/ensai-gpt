import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session

class MenuUtilisateurVue(VueAbstraite):
    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        try:
            print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")
            choix = inquirer.select(
                message="Faites votre choix : ",
                choices=[
                    "Démarrer un chat",
                    "Reprendre un chat",
                    "Infos de session",
                    "Se déconnecter",
                ],
            ).execute()

            if choix == "Se déconnecter":
                Session().deconnexion()
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue("Déconnecté. À bientôt !")

            if choix == "Infos de session":
                return MenuUtilisateurVue(Session().afficher())

            if choix == "Démarrer un chat":
                from view.reponse_ia_vue import ReponseIAVue  # import local
                text = inquirer.text(message="Que veux-tu savoir ?").execute()
                return ReponseIAVue(text)

            if choix == "Reprendre un chat":
                return MenuUtilisateurVue("Reprendre un chat est indisponible pour le moment.")

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[MenuUtilisateurVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.accueil.accueil_vue import AccueilVue
            return AccueilVue("Erreur dans le menu utilisateur (voir terminal).")
