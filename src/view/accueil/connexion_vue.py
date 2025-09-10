from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session
from service.auth_service import AuthService


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (DB)"""

    def choisir_menu(self):
        mail = inquirer.text(message="Email :").execute()
        mdp  = inquirer.secret(message="Mot de passe :").execute()

        user = AuthService().se_connecter(mail, mdp)
        if not user:
            from view.accueil.accueil_vue import AccueilVue
            return AccueilVue("Identifiants invalides ou utilisateur inconnu.")

        # Remplir la Session
        s = Session()
        s.utilisateur = {
            "id_utilisateur": user.id_utilisateur,
            "prenom": user.prenom,
            "nom": user.nom,
            "mail": user.mail,
        }
        s.session = None

        from view.menu_utilisateur_vue import MenuUtilisateurVue
        return MenuUtilisateurVue(f"Bienvenue {user.prenom} !")
