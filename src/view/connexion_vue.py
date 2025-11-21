from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.utilisateur_service import UtilisateurService
from view.accueil_vue import AccueilVue


class ConnexionVue(VueAbstraite):
    """Vue de Connexion"""

    def afficher(self):
        pass

    def choisir_menu(self):
        def quitter_si_vide(val: str):
            if not (val or "").strip():
                raise KeyboardInterrupt

        try:
            user_svc = UtilisateurService()

            mail = (
                (
                    inquirer.text(
                        message="Email (Entrée vide pour quitter) :"
                    ).execute()
                    or ""
                )
                .strip()
                .lower()
            )
            quitter_si_vide(mail)

            if not user_svc.mail_deja_utilise(mail):
                return AccueilVue(
                    "Aucun compte ne correspond à cet email. Créez un compte."
                )

            MAX_TRIES = 3
            for i in range(1, MAX_TRIES + 1):
                mdp = (
                    inquirer.secret(
                        message=f"Mot de passe (essai {i}/{MAX_TRIES}, Entrée vide pour quitter) :"
                    ).execute()
                    or ""
                )
                quitter_si_vide(mdp)

                user = user_svc.se_connecter(mail, mdp)

                if user is not None:
                    s = Session()
                    s.utilisateur = {
                        "id_utilisateur": user.id_utilisateur,
                        "prenom": user.prenom,
                        "nom": user.nom,
                        "mail": user.mail,
                    }
                    s.session = None
                    from view.menu_utilisateur_vue import MenuUtilisateurVue

                    return MenuUtilisateurVue(f"Bienvenue {user.prenom} {user.nom}!")

                # Mot de passe incorrect
                if i < MAX_TRIES:
                    print("Mot de passe incorrect. Réessayez.\n")
                else:
                    return AccueilVue("Mot de passe incorrect (3 tentatives).")

        except KeyboardInterrupt:
            return AccueilVue("Connexion annulée. Retour à l'accueil.")
        except Exception as e:
            print("[ConnexionVue] Exception:", repr(e))
            return AccueilVue("Erreur technique pendant la connexion (voir terminal).")
