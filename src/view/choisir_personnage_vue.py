from __future__ import annotations
import traceback
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from service.session_service import SessionService
from service.personnage_service import PersonnageService
from service.conversation_service import ConversationService
from view.menu_utilisateur_vue import MenuUtilisateurVue
from view.reponse_ia_vue import ReponseIAVue


class ChoisirPersonnageVue(VueAbstraite):
    def __init__(
        self,
        message: str = "",
        session_svc: SessionService | None = None,
        perso_svc: PersonnageService | None = None,
        conv_svc: ConversationService | None = None,
    ) -> None:
        super().__init__(message=message)
        self.session_svc = session_svc or SessionService()
        self.perso_svc = perso_svc or PersonnageService()
        self.conv_svc = conv_svc or ConversationService()

    def afficher(self):
        if self.message:
            print(self.message)
            print()

    def choisir_menu(self):
        try:
            uid = self.session_svc.get_user_id()
            persos = self.perso_svc.list_for_user(uid)
            if not persos:
                return MenuUtilisateurVue("Aucun personnage disponible. Créez-en un d'abord.")

            # 1) Sélection du personnage (+ option Retour)
            choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos] + ["Retour"]
            label = inquirer.select(message="Choisir un personnage :", choices=choices).execute()

            if label == "Quitter":
                return MenuUtilisateurVue("Retour au menu.")

            pid = int(label.split("#")[-1].rstrip(")"))
            perso = next(p for p in persos if p.id_personnageIA == pid)

            # 2) Mémoriser le personnage en session
            self.session_svc.set_personnage(pid=pid, name=perso.name, system_prompt=perso.system_prompt)

            # 3) Titre
            default_title = f"Chat avec {perso.name}"
            titre = (inquirer.text(message="Titre de la conversation :", default=default_title).execute() or "").strip() or default_title

            # 4) Mode (+ option Retour)
            mode = inquirer.select(
                message="Voulez-vous un chat privé ou collaboratif ?",
                choices=["Privé", "Collaboratif", "Retour"],
            ).execute()

            if mode == "Quitter":
                return MenuUtilisateurVue("Retour au menu.")

            is_collab = (mode == "Collaboratif")

            # 5) Création de la conversation via le SERVICE
            conv = self.conv_svc.start(
                id_user=uid,
                personnage={"id_personnageIA": pid, "system_prompt": perso.system_prompt, "name": perso.name},
                titre=titre,
                is_collab=is_collab,
            )

            # 6) Infos conversation en session
            self.session_svc.set_conversation_info(
                cid=conv.id_conversation,
                titre=titre,
                is_collab=bool(getattr(conv, "is_collab", False)),
                token=getattr(conv, "token_collab", None),
            )

            # 7) Première question (Entrée vide pour quitter)
            texte = inquirer.text(
                message=f"[{perso.name}] Première question ? (Entrée vide pour quitter) :"
            ).execute() or ""
            if not texte.strip():
                return MenuUtilisateurVue("Conversation annulée.")

            return ReponseIAVue(texte)

        except Exception as e:
            print("\n[ChoisirPersonnageVue] Exception :", repr(e))
            print(traceback.format_exc())
            return MenuUtilisateurVue("Erreur pendant la sélection du personnage (voir logs).")
