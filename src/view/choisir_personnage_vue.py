from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session
from src.dao.personnage_ia_dao import PersonnageIADao

class ChoisirPersonnageVue(VueAbstraite):
    """
    Liste les personnages standards + ceux créés par l'utilisateur.
    Met à jour la Session().personnage et enchaîne vers la question utilisateur.
    """
    def __init__(self, message: str = ""):
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        s = Session()
        uid = s.utilisateur.get("id_utilisateur")
        dao = PersonnageIADao()
        persos = dao.list_for_user(uid)

        if not persos:
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Aucun personnage disponible. Créez-en un d'abord.")

        choices = [f"{p.name} (#{p.id_personnageIA})" for p in persos]
        label = inquirer.select(
            message="Choisir un personnage :",
            choices=choices,
        ).execute()

        # retrouver l'objet choisi
        pid = int(label.split("#")[-1].rstrip(")"))
        perso = next(p for p in persos if p.id_personnageIA == pid)

        s.personnage = {
            "id_personnageIA": perso.id_personnageIA,
            "name": perso.name,
            "system_prompt": perso.system_prompt,
        }

        # poser la première question
        texte = inquirer.text(message=f"[{perso.name}] Que veux-tu demander ?").execute()
        from view.reponse_ia_vue import ReponseIAVue
        return ReponseIAVue(texte)
