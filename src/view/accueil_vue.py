from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session


class AccueilVue(VueAbstraite):
    """Vue d'accueil de l'application"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Choix du menu suivant"""
        print("\n" + "-" * 50 + "\nAccueil\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Se connecter",
                "Créer un compte",
                "Ré-initialiser la base de données",
                "Quitter",
            ],
        ).execute()

        match choix:
            case "Quitter":
                return  # fin

            case "Se connecter":
                from view.connexion_vue import ConnexionVue  # import local
                return ConnexionVue()

            case "Créer un compte":
                from view.inscription_vue import InscriptionVue  # import local
                return InscriptionVue()

            case "Ré-initialiser la base de données":
                succes = ResetDatabase().lancer()
                message = f"Ré-initialisation de la base de données — {'SUCCÈS' if succes else 'ÉCHEC'}"
                return AccueilVue(message)
