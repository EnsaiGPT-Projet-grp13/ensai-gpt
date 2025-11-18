import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from view.menu_utilisateur_vue import MenuUtilisateurVue
from service.utilisateur_service import UtilisateurService
from view.creer_personnage_vue import CreerPersonnageVue  # Importer la vue pour créer un personnage
from dao.personnage_ia_dao import PersonnageIADao

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
                        "Changer e-mail",
                        "Annuler",
                    ],
                ).execute()

                # ---- Changer mot de passe ----
                if sous == "Changer mot de passe":
                    s = Session()
                    id_utilisateur = s.utilisateur.get("id_utilisateur")

                    ancien = inquirer.secret(
                        message="Ancien mot de passe :"
                    ).execute()
                    nouveau = inquirer.secret(
                        message="Nouveau mot de passe :"
                    ).execute()
                    confirmation = inquirer.secret(
                        message="Confirmez le nouveau mot de passe :"
                    ).execute()

                    if nouveau != confirmation:
                        return ParametresVue("Les mots de passe ne correspondent pas.")

                    svc = UtilisateurService()
                    ok = svc.changer_mot_de_passe(id_utilisateur, ancien, nouveau)

                    if ok:
                        return ParametresVue("Mot de passe modifié avec succès.")
                    else:
                        return ParametresVue("Ancien mot de passe incorrect.")

                # ---- Changer nom utilisateur ----
                if sous == "Changer nom utilisateur":
                    s = Session()
                    id_utilisateur = s.utilisateur.get("id_utilisateur")

                    nouveau_nom = inquirer.text(
                        message="Nouveau nom d'utilisateur :"
                    ).execute()

                    svc = UtilisateurService()
                    ok = svc.changer_nom_utilisateur(id_utilisateur, nouveau_nom)

                    if ok:
                        return ParametresVue(
                            f"Nom d'utilisateur modifié avec succès : {nouveau_nom}"
                        )
                    else:
                        return ParametresVue(
                            "Erreur lors de la modification du nom d'utilisateur."
                        )

                # ---- Changer e-mail ----
                if sous == "Changer e-mail":
                    s = Session()
                    mail = s.utilisateur.get("mail")

                    nouvel_email = inquirer.text(
                        message="Nouvel e-mail :"
                    ).execute()

                    svc = UtilisateurService()
                    ok = svc.changer_email(mail, nouvel_email)

                    if ok:
                        return ParametresVue(
                            f"E-mail modifié avec succès : {nouvel_email}"
                        )
                    else:
                        return ParametresVue(
                            "Erreur lors de la modification de l'e-mail."
                        )

                if sous == "Annuler":
                    return MenuUtilisateurVue()

            # -----------------------------
            # Paramètres Personnages IA
            # -----------------------------
            if choix == "Paramètres personnages IA":
                sous = inquirer.select(
                    message="Choisir une option :",
                    choices=[
                        "Supprimer un personnage IA existant",
                        "Créer un nouveau personnage IA",  # Nouvelle option pour créer un personnage
                        "description des personnages existants",  # Option pour afficher la liste des personnages
                        "Annuler",  # Option pour annuler
                    ],
                ).execute()
                if sous == "Supprimer un personnage IA existant":
                    s = Session()
                    uid = s.utilisateur.get("id_utilisateur")
                    dao = PersonnageIADao()

                    while True:
                        # On ne propose à la suppression que les personnages créés par l'utilisateur
                        persos = dao.list_by_creator(uid)

                        if not persos:
                            return MenuUtilisateurVue(
                                "Vous n'avez aucun personnage IA à supprimer."
                            )

                        choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos]
                        choices.append("Annuler")

                        label = inquirer.select(
                            message="Choisir le personnage IA à supprimer :",
                            choices=choices,
                        ).execute()

                        if label == "Annuler":
                            return MenuUtilisateurVue("Suppression annulée.")

                        # Récupérer l'id à partir du label "Nom (#id)"
                        pid = int(label.split("#")[-1].rstrip(")"))
                        perso = next(p for p in persos if p.id_personnageIA == pid)

                        confirm = inquirer.confirm(
                            message=f"Confirmer la suppression du personnage « {perso.name} » ?",
                            default=False,
                        ).execute()

                        if not confirm:
                            # On redemande si on veut revenir au menu
                            retour = inquirer.confirm(
                                message="Annuler la suppression et revenir au menu ?",
                                default=True,
                            ).execute()
                            if retour:
                                return MenuUtilisateurVue("Suppression annulée.")
                            else:
                                # On reboucle pour choisir à nouveau un personnage
                                continue

                        ok = dao.delete(pid)
                        if ok:
                            return MenuUtilisateurVue(
                                f"Personnage « {perso.name} » supprimé avec succès."
                            )
                        else:
                            return MenuUtilisateurVue(
                                "Impossible de supprimer ce personnage IA car des conversations y sont encore associées.\n"
                                "Supprimez d'abord les conversations correspondantes dans l'historique, puis réessayez."
                            )
                if sous == "Créer un nouveau personnage IA":
                    # Rediriger vers la vue de création d'un personnage IA
                    return CreerPersonnageVue(
                        message="Créer un nouveau personnage IA.",
                        session_svc=None,  # Ajoutez ici les services nécessaires (comme session_svc et perso_svc)
                        perso_svc=None     # Idem
                    )

                if sous == "description des personnages existants":
                    # On reste dans choisir_menu, sans def séparée
                    s = Session()
                    uid = s.utilisateur.get("id_utilisateur")
                    dao = PersonnageIADao()

                    while True:
                        persos = dao.list_for_user(uid)

                        if not persos:
                            return MenuUtilisateurVue(
                                "Aucun personnage disponible. Créez-en un d'abord."
                            )

                        choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos]
                        choices.append("Retour")

                        label = inquirer.select(
                            message="Choisir un personnage pour consulter sa description :",
                            choices=choices
                        ).execute()

                        if label == "Retour":
                            return MenuUtilisateurVue("Retour au menu des paramètres.")

                        pid = int(label.split("#")[-1].rstrip(")"))
                        perso = next(p for p in persos if p.id_personnageIA == pid)

                        print(f"\nDescription du personnage '{perso.name}':\n")
                        print(f"{perso.system_prompt}\n")
                        # La boucle recommence pour permettre d'en consulter un autre

                if sous == "Annuler":
                    return MenuUtilisateurVue()

            if choix == "Annuler":
                return MenuUtilisateurVue()

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[ParametresVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur dans le menu des paramètres.")
