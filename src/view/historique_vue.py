from view.vue_abstraite import VueAbstraite
from view.session import Session
from src.service.conversation_service import ConversationService
from InquirerPy import inquirer
import traceback

class HistoriqueVue(VueAbstraite):
    def __init__(self, message: str = ""):
        self.message = message
        self.service = ConversationService()

    def afficher(self):
        if self.message:
            print(self.message)

    def _print_table(self, convs):
        if not convs:
            print("Aucune conversation.")
            return

        # entêtes
        headers = ["Titre", "PersonnageID", "Créée", "MAJ"]
        # largeurs colonnes minimales
        w_id, w_titre, w_perso, w_created, w_updated = 6, 32, 12, 19, 19

        def trunc(s: str, w: int) -> str:
            s = s or ""
            return (s[: w-1] + "…") if len(s) > w else s

        line = (
            f"{'ID'.ljust(w_id)} | "
            f"{'Titre'.ljust(w_titre)} | "
            f"{'PersoID'.ljust(w_perso)} | "
            f"{'Créée'.ljust(w_created)} | "
            f"{'MAJ'.ljust(w_updated)}"
        )
        sep = "-" * len(line)
        print(sep)
        print(line)
        print(sep)

        for c in convs:
            titre = trunc(c.titre or "(sans titre)", w_titre)
            created = (str(c.created_at)[:19]) if c.created_at else ""
            updated = (str(c.updated_at)[:19]) if c.updated_at else ""
            print(
                f"{str(c.id_conversation).ljust(w_id)} | "
                f"{titre.ljust(w_titre)} | "
                f"{str(c.id_personnageIA).ljust(w_perso)} | "
                f"{created.ljust(w_created)} | "
                f"{updated.ljust(w_updated)}"
            )
        print(sep)

    def choisir_menu(self):
        try:
            s = Session()
            if not s.utilisateur:
                from view.menu_utilisateur_vue import MenuUtilisateurVue
                return MenuUtilisateurVue("Connecte-toi d'abord.")

            convs = self.service.list_for_user(s.utilisateur["id_utilisateur"], limit=100)
            print("\n=== Historique des conversations ===\n")
            self._print_table(convs)
            # simple pause puis retour menu
            inquirer.text(message="Appuie sur Entrée pour revenir au menu.").execute()
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue()

        except Exception as e:
            print("\n[HistoriqueVue] Exception :", repr(e))
            print(traceback.format_exc())
            from view.menu_utilisateur_vue import MenuUtilisateurVue
            return MenuUtilisateurVue("Erreur lors de l'affichage de l'historique (voir terminal).")
