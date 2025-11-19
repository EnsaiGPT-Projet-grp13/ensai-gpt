import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from view.menu_utilisateur_vue import MenuUtilisateurVue
from service.personnage_service import PersonnageService
from view.creer_personnage_vue import CreerPersonnageVue


class ParametresPersoIAVue(VueAbstraite):
    """Vue pour gérer les paramètres des personnages IA."""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        try:
            self.afficher()
            print("\n" + "-" * 50 + "\nParamètres personnages IA\n" + "-" * 50 + "\n")

            sous = inquirer.select(
                message="Choisir une option :",
                choices=[
                    "Supprimer un personnage IA existant",
                    "Créer un nouveau personnage IA",
                    "Description des personnages existants",
                    "Annuler",
                ],
            ).execute()

            s = Session()
            uid = s.utilisateur.get("id_utilisateur")
            svc = PersonnageService()


            if sous == "Supprimer un personnage IA existant":
                while True:
                    persos = svc.lister_personnages_ia_crees_par(uid)

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

                    pid = int(label.split("#")[-1].rstrip(")"))
                    perso = next(p for p in persos if p.id_personnageIA == pid)

                    confirm = inquirer.confirm(
                        message=f"Confirmer la suppression du personnage « {perso.name} » ?",
                        default=False,
                    ).execute()

                    if not confirm:
                        retour = inquirer.confirm(
                            message="Annuler la suppression et revenir au menu ?",
                            default=True,
                        ).execute()
                        if retour:
                            return MenuUtilisateurVue("Suppression annulée.")
                        else:
                            # on reboucle
                            continue

                    ok = svc.supprimer_personnage_ia(uid, pid)

                    if ok:
                        return MenuUtilisateurVue(
                            f"Personnage « {perso.name} » supprimé avec succès."
                        )
                    else:
                        return MenuUtilisateurVue(
                            "Impossible de supprimer ce personnage IA (il n'appartient pas à cet utilisateur ou une erreur est survenue)."
                        )


            if sous == "Créer un nouveau personnage IA":
                # À adapter si tu veux vraiment injecter des services
                return CreerPersonnageVue(
                    message="Créer un nouveau personnage IA.",
                    session_svc=None,
                    perso_svc=None,
                )

            if sous == "Description des personnages existants":
                while True:
                    persos = svc.lister_personnages_ia_pour_utilisateur(uid)

                    if not persos:
                        return MenuUtilisateurVue(
                            "Aucun personnage disponible. Créez-en un d'abord."
                        )

                    choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos]
                    choices.append("Retour")

                    label = inquirer.select(
                        message="Choisir un personnage pour consulter sa description :",
                        choices=choices,
                    ).execute()

                    if label == "Retour":
                        return MenuUtilisateurVue("Retour au menu des paramètres.")

                    pid = int(label.split("#")[-1].rstrip(")"))
                    perso = next(p for p in persos if p.id_personnageIA == pid)

                    print(f"\nDescription du personnage '{perso.name}':\n")
                    print(f"{perso.system_prompt}\n")
                    # reboucle pour en consulter un autre


            if sous == "Annuler":
                return MenuUtilisateurVue()

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[ParametresPersoIAVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur dans les paramètres personnages IA.")
