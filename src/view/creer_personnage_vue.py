from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session
from src.dao.personnage_ia_dao import PersonnageIADao
from src.objects.personnage_ia import PersonnageIA

class CreerPersonnageVue(VueAbstraite):
    def __init__(self, message: str = ""):
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        s = Session()
        uid = s.utilisateur.get("id_utilisateur")

        name = inquirer.text(message="Nom du personnage :").execute().strip()
        if not name:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Nom invalide.")

        prompt = inquirer.text(
            message="Prompt système (rôle, style, limites, format de réponse) :"
        ).execute().strip()
        if not prompt:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Prompt système vide.")

        dao = PersonnageIADao()
        perso = dao.create(PersonnageIA(
            id_personnageIA=None,
            name=name,
            system_prompt=prompt,
            created_by=uid
        ))

        s.personnage = {
            "id_personnageIA": perso.id_personnageIA,
            "name": perso.name,
            "system_prompt": perso.system_prompt,
        }

        default_title = f"Chat avec {perso.name}"
        titre = inquirer.text(message="Titre de la conversation :", default=default_title).execute().strip()
        s.conversation_title = titre or default_title

        # Première question
        texte = inquirer.text(message=f"[{perso.name}] Première question ?").execute()
        from view.reponse_ia_vue import ReponseIAVue
        return ReponseIAVue(texte)
