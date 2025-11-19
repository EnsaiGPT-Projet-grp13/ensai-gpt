# view/parametres_utilisateur_vue.py

import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from service.utilisateur_service import UtilisateurService
from view.menu_utilisateur_vue import MenuUtilisateurVue


class ParametresUtilisateurVue(VueAbstraite):
    """Vue pour gérer les paramètres utilisateur (mdp, identité, email)."""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        try:
            self.afficher()
            print("\n" + "-" * 50 + "\nParamètres utilisateur\n" + "-" * 50 + "\n")

            choix = inquirer.select(
                message="Choisir une option :",
                choices=[
                    "Changer mot de passe",
                    "Changer identité (prénom + nom)",
                    "Changer e-mail",
                    "Retour",
                ],
            ).execute()

            s = Session()
            uid = s.utilisateur.get("id_utilisateur")
            mail = s.utilisateur.get("mail")
            svc = UtilisateurService()

            # -----------------------------
            # Changer mot de passe
            # -----------------------------
            if choix == "Changer mot de passe":
                ancien = inquirer.secret(
                    message="Ancien mot de passe :"
                ).execute() or ""

                nouveau = inquirer.secret(
                    message="Nouveau mot de passe :"
                ).execute() or ""

                confirmation = inquirer.secret(
                    message="Confirmez le nouveau mot de passe :"
                ).execute() or ""

                if nouveau != confirmation:
                    return ParametresUtilisateurVue("Les mots de passe ne correspondent pas.")

                ok, msg = svc.changer_mot_de_passe(uid, ancien, nouveau)
                return ParametresUtilisateurVue(msg)

            # -----------------------------
            # Changer identité (prénom + nom)
            # -----------------------------
            if choix == "Changer identité (prénom + nom)":
                nouveau_prenom = inquirer.text(
                    message="Nouveau prénom :"
                ).execute() or ""

                nouveau_nom = inquirer.text(
                    message="Nouveau nom :"
                ).execute() or ""

                ok, msg = svc.changer_identite(uid, nouveau_prenom, nouveau_nom)
                return ParametresUtilisateurVue(msg)

            # -----------------------------
            # Changer e-mail
            # -----------------------------
            if choix == "Changer e-mail":
                nouvel_email = inquirer.text(
                    message="Nouvel e-mail (Entrée vide pour annuler) :"
                ).execute() or ""

                if not nouvel_email.strip():
                    return ParametresUtilisateurVue("Changement d'e-mail annulé.")

                mdp = inquirer.secret(
                    message="Mot de passe actuel (Entrée vide pour annuler) :"
                ).execute() or ""

                if not mdp:
                    return ParametresUtilisateurVue("Changement d'e-mail annulé.")

                ok, msg = svc.changer_email(uid, nouvel_email, mdp)
                return ParametresUtilisateurVue(msg)

            # -----------------------------
            # Retour
            # -----------------------------
            if choix == "Retour":
                return MenuUtilisateurVue()

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[ParametresUtilisateurVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur dans les paramètres utilisateur.")
