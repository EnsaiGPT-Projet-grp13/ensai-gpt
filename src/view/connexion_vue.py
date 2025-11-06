from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.auth_service import AuthService


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (DB)"""

    def afficher(self):
        pass
    
    def choisir_menu(self):
        try:
            # dans ConnexionVue
            mail = inquirer.text(message="Email :").execute().strip().lower()
            auth = AuthService()
            user = auth.find_user(mail)

            if not user:
                from view.accueil_vue import AccueilVue
                return AccueilVue("Aucun compte ne correspond à cet email. Créez un compte.")

            # 3 essais pour le mot de passe
            MAX_TRIES = 3
            for i in range(1, MAX_TRIES + 1):
                mdp = inquirer.secret(message=f"Mot de passe (essai {i}/{MAX_TRIES}) :").execute()
                if auth.check_password(user, mdp):
                    # succès -> remplir la session et aller au menu utilisateur
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

                # mauvais mdp -> si essai restant, on réessaie
                if i < MAX_TRIES:
                    print("Mot de passe incorrect. Réessayez.")
                else:
                    from view.accueil_vue import AccueilVue
                    return AccueilVue("Mot de passe incorrect (3 tentatives).")

        except Exception as e:
            # log console pour éviter le retour silencieux
            print("[ConnexionVue] Exception:", repr(e))
            from view.accueil_vue import AccueilVue
            return AccueilVue("Erreur technique pendant la connexion (voir terminal).")

