import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.menu_utilisateur_vue import MenuUtilisateurVue


class ParametresVue(VueAbstraite):
    """Vue pour gérer le menu principal des paramètres."""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        try:
            self.afficher()
            print("\n" + "-" * 50 + "\nParamètres\n" + "-" * 50 + "\n")

            choix = inquirer.select(
                message="Faites votre choix : ",
                choices=[
                    "Paramètres utilisateur",
                    "Paramètres personnages IA",
                    "Annuler",
                ],
            ).execute()

            if choix == "Paramètres utilisateur":
                from view.parametres_utilisateur_vue import ParametresUtilisateurVue

                return ParametresUtilisateurVue()

            if choix == "Paramètres personnages IA":
                from view.parametres_perso_ia_vue import ParametresPersoIAVue

                return ParametresPersoIAVue()

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[ParametresVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur dans le menu des paramètres.")
