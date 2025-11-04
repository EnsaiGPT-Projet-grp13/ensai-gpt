from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from src.service.utilisateur_service import UtilisateurService


class RechercheConversationTitreVue(VueAbstraite):
    """Vue des options au sujet de l'historique de l'application"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Insertion du titre recherché"""
        print("\n" + "-" * 50 + "\nHistorique\n" + "-" * 50 + "\n")

        s = Session()
        id_utilisateur = s.utilisateur.get("id_utilisateur")
        service = UtilisateurService()
        conversations = service.list_for_user(id_utilisateur)
        if not conversations:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Aucun personnage disponible. Créez-en un d'abord.")

        choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos]
        label = inquirer.select(message="Choisir un personnage :", choices=choices).execute()
        pid = int(label.split("#")[-1].rstrip(")"))
        perso = next(p for p in persos if p.id_personnageIA == pid)

        s.personnage = {
            "id_personnageIA": perso.id_personnageIA,
            "name": perso.name,
            "system_prompt": perso.system_prompt,
        }

        default_title = f"Chat avec {perso.name}"
        titre = inquirer.text(message="Titre de la conversation :", default=default_title).execute().strip()
        s.conversation_title = titre or default_title

        import secrets  # pour générer le token

        mode = inquirer.select(
            message="Voulez-vous un chat privé ou collaboratif ?",
            choices=["Privé", "Collaboratif"],
        ).execute()

        s.conversation_is_collab = (mode == "Collaboratif")

        if s.conversation_is_collab:
            s.conversation_token = secrets.token_urlsafe(16)
        else:
            s.conversation_token = None

        # Première question
        texte = inquirer.text(message=f"[{perso.name}] Première question ?").execute()
        from view.reponse_ia_vue import ReponseIAVue
        return ReponseIAVue(texte)
