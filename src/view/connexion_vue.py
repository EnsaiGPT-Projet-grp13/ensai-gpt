from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.auth_service import AuthService
from view.accueil_vue import AccueilVue


class ConnexionVue(VueAbstraite):
    """Vue de Connexion (DB)"""

    def afficher(self):
        pass

    def choisir_menu(self):
        def quitter_si_vide(val: str):
            if not (val or "").strip():
                raise KeyboardInterrupt

        try:
            # --- Email ---
            mail = (inquirer.text(message="Email (Entrée vide pour quitter) :").execute() or "").strip().lower()
            quitter_si_vide(mail)

            auth = AuthService()
            user = auth.find_user(mail)
            if not user:
                return AccueilVue("Aucun compte ne correspond à cet email. Créez un compte.")

            # --- Mot de passe (3 essais) ---
            MAX_TRIES = 3
            for i in range(1, MAX_TRIES + 1):
                mdp = inquirer.secret(message=f"Mot de passe (essai {i}/{MAX_TRIES}, Entrée vide pour quitter) :").execute() or ""
                quitter_si_vide(mdp)

                if auth.check_password(user, mdp):
                    # succès -> remplir la session et aller au menu utilisateur
                    s = Session()
                    s.utilisateur = {
                        "id_utilisateur": user.id_utilisateur,
                        "prenom": user.prenom,
                        "nom": user.nom,
                        "mail": user.mail,
                        # optionnel: préférences si présentes en DB
                        "temperature": getattr(user, "temperature", 0.7),
                        "top_p": getattr(user, "top_p", 1.0),
                        "max_tokens": getattr(user, "max_tokens", 150),
                    }
                    s.session = None
                    from view.menu_utilisateur_vue import MenuUtilisateurVue
                    return MenuUtilisateurVue(f"Bienvenue {user.prenom} {user.nom}!")

                if i < MAX_TRIES:
                    print("Mot de passe incorrect. Réessayez.\n")
                else:
                    return AccueilVue("Mot de passe incorrect (3 tentatives).")

        except KeyboardInterrupt:
            return AccueilVue("Connexion annulée. Retour à l'accueil.")
        except Exception as e:
            print("[ConnexionVue] Exception:", repr(e))
            return AccueilVue("Erreur technique pendant la connexion (voir terminal).")

