import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session
from view.menu_utilisateur_vue import MenuUtilisateurVue
from service.utilisateur_service import UtilisateurService
from src.dao.personnage_ia_dao import PersonnageIADao


class ParametresVue(VueAbstraite):
    """Vue pour gérer les paramètres utilisateur et personnages IA."""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    # -------------------------------------------------
    
    # -------------------------------------------------
    def choisir_persoIA(self):
        """Permet à l'utilisateur de choisir un personnage IA."""
        try:
            s = Session()
            uid = s.utilisateur.get("id_utilisateur")
            dao = PersonnageIADao()
            persos = dao.list_for_user(uid)

            if not persos:
                return MenuUtilisateurVue("Aucun personnage disponible. Créez-en un d'abord.")

            choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos]
            choices.append("Annuler")  # ✅ ajoute une option d’annulation

            label = inquirer.select(
                message="Choisir un personnage :",
                choices=choices
            ).execute()

            # Si l'utilisateur choisit "Annuler", on retourne simplement au menu principal
            if label == "Annuler":
                return MenuUtilisateurVue("Retour au menu des paramètres.")

            pid = int(label.split("#")[-1].rstrip(")"))
            perso = next(p for p in persos if p.id_personnageIA == pid)

            s.personnage = {
                "id_personnageIA": perso.id_personnageIA,
                "name": perso.name,
                "system_prompt": perso.system_prompt,
            }

            return MenuUtilisateurVue(f"✅ Personnage '{perso.name}' sélectionné.")

        except Exception as e:
            print("\n[ParametresVue.choisir_persoIA] Exception :", repr(e))
            print(traceback.format_exc())
            return ParametresVue("Erreur lors du choix du personnage IA.")

    # -------------------------------------------------
    
    # -------------------------------------------------
    def choisir_menu(self):
        """Affiche le menu principal des paramètres."""
        try:
            print("\n" + "-" * 50 + "\nParamètres\n" + "-" * 50 + "\n")

            choix = inquirer.select(
                message="Faites votre choix : ",
                choices=[
                    "Gérer paramètres utilisateur",
                    "Gérer paramètres personnages IA"
                ],
            ).execute()

            # -----------------------------
            # Paramètres utilisateur
            # -----------------------------
            if choix == "Gérer paramètres utilisateur":
                sous = inquirer.select(
                    message="Choisir une option :",
                    choices=[
                        "Changer mot de passe",
                        "Changer nom utilisateur",
                        "Annuler",
                    ],
                ).execute()

                if sous == "Changer mot de passe":
                    return self.changer_mot_de_passe()

                if sous == "Changer nom utilisateur":
                    # (Tu pourras l’ajouter plus tard)
                    return ParametresVue("🚧 Fonctionnalité en cours de développement.")

            # -----------------------------
            # Paramètres Personnages IA
            # -----------------------------
            if choix == "Gérer paramètres personnages IA":
                return self.choisir_persoIA()

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[MenuUtilisateurVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.accueil_vue import AccueilVue
            return AccueilVue("Erreur dans le menu utilisateur (voir terminal).")

    # -------------------------------------------------
    # 🔐 Changement de mot de passe
    # -------------------------------------------------
    def changer_mot_de_passe(self):
        """Permet à l'utilisateur connecté de changer son mot de passe."""
        try:
            s = Session()
            uid = s.utilisateur.get("id_utilisateur")

            ancien = inquirer.secret(message="Ancien mot de passe :").execute()
            nouveau = inquirer.secret(message="Nouveau mot de passe :").execute()
            confirmation = inquirer.secret(message="Confirmer le nouveau mot de passe :").execute()

            if nouveau != confirmation:
                return ParametresVue(" Les mots de passe ne correspondent pas.")

            service = UtilisateurService()
            if service.changer_mot_de_passe(uid, ancien, nouveau):
                return ParametresVue(" Mot de passe modifié avec succès.")
            else:
                return ParametresVue(" Ancien mot de passe incorrect.")

        except Exception as e:
            print("\n[ParametresVue] Erreur :", repr(e))
            print(traceback.format_exc())
            return ParametresVue("Erreur lors du changement de mot de passe.")
