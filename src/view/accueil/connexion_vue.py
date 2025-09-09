from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from service.utilisateur_service import UtilisateurService


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (saisie de mail et mdp)"""

    def choisir_menu(self):
        # Saisie
        mail = inquirer.text(message="Entrez votre e-mail : ").execute()
        mdp = inquirer.secret(message="Entrez votre mot de passe : ").execute()

        # Auth via service
        utilisateur = UtilisateurService().se_connecter(mail, mdp)

        if utilisateur:
            # Remplir la Session
            s = Session()
            s.utilisateur = {
                "id_utilisateur": utilisateur.id_utilisateur,
                "prenom": utilisateur.prenom,
                "nom": utilisateur.nom,
                "mail": utilisateur.mail,
            }
            # ⚠️ On RETOURNE la vue suivante, on ne l'exécute pas ici
            from view.menu_utilisateur_vue import MenuUtilisateurVue  # import local pour éviter les cycles
            message = f"Vous êtes connecté en tant que {utilisateur.prenom} {utilisateur.nom}"
            return MenuUtilisateurVue(message)

        # Échec : retour accueil avec message
        from view.accueil.accueil_vue import AccueilVue
        return AccueilVue("Erreur de connexion (e-mail ou mot de passe invalide)")
