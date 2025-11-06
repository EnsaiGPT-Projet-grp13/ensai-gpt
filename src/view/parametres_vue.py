import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from view.menu_utilisateur_vue import MenuUtilisateurVue
from service.utilisateur_service import UtilisateurService
from view.creer_personnage_vue import CreerPersonnageVue  # Importer la vue pour créer un personnage
from src.dao.personnage_ia_dao import PersonnageIADao

class ParametresVue(VueAbstraite):
    """Vue pour gérer les paramètres utilisateur et personnages IA."""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Affiche le menu principal des paramètres."""
        try:
            print("\n" + "-" * 50 + "\nParamètres\n" + "-" * 50 + "\n")

            choix = inquirer.select(
                message="Faites votre choix : ",
                choices=[
                    "Paramètres utilisateur",
                    "Paramètres personnages IA",  # Nouvelle option ajoutée pour gérer les personnages IA
                    "Annuler",
                ],
            ).execute()

            # -----------------------------
            # Paramètres utilisateur
            # -----------------------------
            if choix == "Paramètres utilisateur":
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
                    return ParametresVue("🚧 Fonctionnalité en cours de développement.")

            # -----------------------------
            # Paramètres Personnages IA
            # -----------------------------
            if choix == "Paramètres personnages IA":
                sous = inquirer.select(
                    message="Choisir une option :",
                    choices=[
                        "Créer un nouveau personnage IA",  # Nouvelle option pour créer un personnage
                        "Voir la liste des personnages IA",  # Option pour afficher la liste des personnages
                        "Annuler",  # Option pour annuler
                    ],
                ).execute()

                if sous == "Créer un nouveau personnage IA":
                    # Rediriger vers la vue de création d'un personnage IA
                    return CreerPersonnageVue(
                        message="Créer un nouveau personnage IA.",
                        session_svc=None,  # Ajoutez ici les services nécessaires (comme session_svc et perso_svc)
                        perso_svc=None     # Idem
                    )

                if sous == "Voir la liste des personnages IA":
                    # Afficher la liste des personnages IA
                    return self.afficher_liste_persoIA()

            if choix == "Annuler":
                return MenuUtilisateurVue()

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[ParametresVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur dans le menu des paramètres.")

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
                return ParametresVue("Les mots de passe ne correspondent pas.")

            service = UtilisateurService()
            if service.changer_mot_de_passe(uid, ancien, nouveau):
                return ParametresVue("Mot de passe modifié avec succès.")
            else:
                return ParametresVue("Ancien mot de passe incorrect.")

        except Exception as e:
            print("\n[ParametresVue] Erreur :", repr(e))
            print(traceback.format_exc())
            return ParametresVue("Erreur lors du changement de mot de passe.")

    # -------------------------------------------------
    # Afficher la liste des personnages IA
    # -------------------------------------------------
    def afficher_liste_persoIA(self):
        """Affiche la liste des personnages IA et permet de consulter leur description (prompt)."""
        try:
            s = Session()
            uid = s.utilisateur.get("id_utilisateur")
            dao = PersonnageIADao()
            persos = dao.list_for_user(uid)

            if not persos:
                return MenuUtilisateurVue("Aucun personnage disponible. Créez-en un d'abord.")

            choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos]
            choices.append("Retour")  # Option de retour

            label = inquirer.select(
                message="Choisir un personnage pour voir sa description :",
                choices=choices
            ).execute()

            # Si l'utilisateur choisit "Retour", on retourne au menu précédent
            if label == "Retour":
                return MenuUtilisateurVue("Retour au menu des paramètres.")

            pid = int(label.split("#")[-1].rstrip(")"))
            perso = next(p for p in persos if p.id_personnageIA == pid)

            # Afficher la description du personnage (son prompt)
            # Utilisation de inquirer.text() pour afficher la description en lecture seule
            inquirer.text(
                message=f"Description du personnage '{perso.name}':",
                default=perso.system_prompt,
                style="bold",
                multiline=True,  # Permet de voir toute la description
                validate=lambda x: True  # Empêche toute modification du texte
            ).execute()

            # Retour à la liste des personnages
            return self.afficher_liste_persoIA()

        except Exception as e:
            print("\n[ParametresVue.afficher_liste_persoIA] Exception :", repr(e))
            print(traceback.format_exc())
            return ParametresVue("Erreur lors de l'affichage des personnages IA.")
