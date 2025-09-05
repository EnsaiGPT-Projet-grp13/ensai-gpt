from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from view.menu_utilisateur_vue import MenuUtilisateurVue

from service.utilisateur_service import UtilisateurService


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (saisie de mail et mdp)"""

    def choisir_menu(self):
        # Demande à l'utilisateur de saisir mail et mot de passe
        mail = inquirer.text(message="Entrez votre e-mail : ").execute()
        mdp = inquirer.secret(message="Entrez votre mot de passe : ").execute()

        # Appel du service pour trouver l'utilisateur
        utilisateur = UtilisateurService().se_connecter(mail, mdp)

        # Si l'utilisateur a été trouvé à partir de ses identifiants
        if utilisateur:
            message = f"Vous êtes connecté en tant que {utilisateur.prenom} {utilisateur.nom}"
                next_vue = MenuUtilisateurVue(message)
                next_vue.afficher()
                return next_vue.choisir_menu()

        message = "Erreur de connexion (e-mail ou mot de passe invalide)"
        from view.accueil.accueil_vue import AccueilVue
        return AccueilVue(message)
    