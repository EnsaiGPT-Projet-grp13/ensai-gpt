from datetime import date
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from service.auth_service import AuthService


class InscriptionVue(VueAbstraite):
    """Vue d'inscription (DB)"""

    def choisir_menu(self):
        prenom = inquirer.text(message="Prénom :").execute()
        nom = inquirer.text(message="Nom :").execute()
        mail = inquirer.text(message="Email :").execute()
        mdp = inquirer.secret(message="Mot de passe :").execute()
        naiss_str = inquirer.text(message="Date de naissance (YYYY-MM-DD) :").execute()

        try:
            naiss = date.fromisoformat(naiss_str)
        except Exception:
            from view.accueil_vue import AccueilVue
            return AccueilVue("Date invalide. Format attendu : YYYY-MM-DD")

        try:
            user = AuthService().inscrire(prenom, nom, mail, mdp, naiss)
        except ValueError as e:
            from view.accueil_vue import AccueilVue
            return AccueilVue(f"Inscription impossible : {e}")

        from view.accueil_vue import AccueilVue
        return AccueilVue(f"Compte créé pour {user.prenom} {user.nom}. Vous pouvez vous connecter.")
