from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from utils.reset_database import ResetDatabase


class AccueilVue(VueAbstraite):
    """Vue d'accueil de l'application"""

    def choisir_menu(self):
        """Choix du menu suivant"""
        print("\n" + "-" * 50 + "\nAccueil\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Se connecter",
                "Créer un compte",
                "Ré-initialiser la base de données",
                "Infos de session",
                "Quitter",
            ],
        ).execute()

        match choix:
            case "Quitter":
                return  # fin

            case "Se connecter":
                # --- Mode sans base : on mock l'authentification ---
                email = inquirer.text(message="Email :").execute()
                _ = inquirer.secret(message="Mot de passe :").execute()

                # On remplit la session avec un utilisateur factice
                s = Session()
                s.utilisateur = {
                    "id_utilisateur": -1,
                    "prenom": (email.split("@")[0] or "User").capitalize(),
                    "nom": "",
                    "mail": email,
                }
                s.session = None  # pas de session DB

                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue(f"Connecté (mode sans base) : {email}")

            case "Créer un compte":
                # En mode sans base, on redirige vers une 'connexion' simple
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue("Création de compte indisponible sans base. Utilisez 'Se connecter'.")

            case "Infos de session":
                return AccueilVue(Session().afficher())

            case "Ré-initialiser la base de données":
                succes = ResetDatabase().lancer()
                message = f"Ré-initilisation de la base de données - {'SUCCES' if succes else 'ECHEC'}"
                return AccueilVue(message)
