from __future__ import annotations
import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from service.session_service import SessionService
from service.personnage_service import PersonnageService
from view.menu_utilisateur_vue import MenuUtilisateurVue
from view.choisir_personnage_vue import ChoisirPersonnageVue


class CreerPersonnageVue(VueAbstraite):
    def __init__(
        self,
        message: str = "",
        session_svc: SessionService | None = None,
        perso_svc: PersonnageService | None = None,
    ) -> None:
        super().__init__(message=message)
        self.session_svc = session_svc or SessionService()
        self.perso_svc = perso_svc or PersonnageService()

    def afficher(self):
        # CONTRAT DU MAIN : afficher() ne renvoie rien
        if self.message:
            print(self.message)
            print()

    def choisir_menu(self):
        try:
            uid = self.session_svc.get_user_id()

            name = inquirer.text(message="Nom du personnage :").execute().strip()
            if not name:
                return MenuUtilisateurVue("Nom invalide.")

            prompt = inquirer.text(
                message="Prompt système (rôle, style, limites, format de réponse) :"
            ).execute().strip()
            if not prompt:
                return MenuUtilisateurVue("Prompt système vide.")

            # Service = crée + lie à l'utilisateur
            perso = self.perso_svc.create_personnage(uid, name, prompt)

            # On n’écrit pas encore le perso en session ici.
            # On renvoie vers la sélection (qui gère correctement la session + conv)
            return ChoisirPersonnageVue(
                message=f"Personnage « {perso.name} » créé. Sélectionnez un personnage :",
                session_svc=self.session_svc,
                perso_svc=self.perso_svc,
            )

        except Exception as e:
            print("\n[CreerPersonnageVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur lors de la création du personnage (voir logs).")
