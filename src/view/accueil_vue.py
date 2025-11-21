from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite


class AccueilVue(VueAbstraite):
    """Vue d'accueil de l'application"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        print("\n" + "-" * 50 + "\nAccueil\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Se connecter",
                "Créer un compte",
                "Quitter",
            ],
        ).execute()

        match choix:
            case "Quitter":
                return

            case "Se connecter":
                from view.connexion_vue import ConnexionVue

                return ConnexionVue()

            case "Créer un compte":
                from view.inscription_vue import InscriptionVue

                return InscriptionVue()

