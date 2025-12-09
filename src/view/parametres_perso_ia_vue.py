import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from objects.session import Session
from view.menu_utilisateur_vue import MenuUtilisateurVue
from service.personnage_service import PersonnageService


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
                    "Modification prompts personnages",
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

                    choices = [
                        {"name": p.name, "value": p.id_personnageIA} for p in persos
                    ]
                    choices.append({"name": "Annuler", "value": None})

                    pid = inquirer.select(
                        message="Choisir le personnage IA à supprimer :",
                        choices=choices,
                    ).execute()

                    if pid is None:
                        return MenuUtilisateurVue("Suppression annulée.")

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
                name = (
                    inquirer.text(
                        message="Nom du personnage (Entrée vide pour annuler) :"
                    ).execute()
                    or ""
                ).strip()
                if not name:
                    return MenuUtilisateurVue("Création annulée.")

                prompt = (
                    inquirer.text(
                        message=(
                            "Prompt système (rôle, style, limites, format de réponse — "
                            "Entrée vide pour annuler) :"
                        )
                    ).execute()
                    or ""
                ).strip()
                if not prompt:
                    return MenuUtilisateurVue("Création annulée.")

                prompt_full = "Tu es le personnage suivant : " + prompt
                perso = svc.create_personnage(uid, name, prompt_full)
                return MenuUtilisateurVue(f"Personnage « {perso.name} » créé.")

            if sous == "Modification prompts personnages":
                while True:
                    persos = svc.lister_personnages_ia_crees_par(uid)

                    if not persos:
                        return MenuUtilisateurVue(
                            "Aucun personnage disponible. Créez-en un d'abord."
                        )

                    choices = [
                        {"name": p.name, "value": p.id_personnageIA} for p in persos
                    ]
                    choices.append({"name": "Retour", "value": None})

                    pid = inquirer.select(
                        message="Choisir un personnage à modifier :",
                        choices=choices,
                    ).execute()

                    if pid is None:
                        return MenuUtilisateurVue("Retour au menu des paramètres.")

                    perso = next(p for p in persos if p.id_personnageIA == pid)

                    print(f"\nModification du prompt de « {perso.name} » :\n")

                    # --- ÉDITION DIRECTE DU PROMPT AVEC VALIDATION PAR ENTRÉE ---
                    nouveau_prompt = (
                        inquirer.text(
                            message="Éditer le prompt puis valider avec Entrée :",
                            default=perso.system_prompt,   # montre l'ancien prompt
                        ).execute()
                        or ""
                    ).strip()

                    if not nouveau_prompt:
                        return MenuUtilisateurVue("Modification annulée.")

                    perso_mod = svc.modifier_system_prompt(uid, pid, nouveau_prompt)

                    if perso_mod is None:
                        return MenuUtilisateurVue(
                            "Impossible de modifier ce prompt."
                        )

                    return MenuUtilisateurVue(
                        f"Prompt du personnage « {perso_mod.name} » mis à jour."
                    )

            if sous == "Annuler":
                return MenuUtilisateurVue()

            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[ParametresPersoIAVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur dans les paramètres personnages IA.")
