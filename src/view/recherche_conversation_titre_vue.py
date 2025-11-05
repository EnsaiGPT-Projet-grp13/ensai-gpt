from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite



class RechercheConversationTitreVue(VueAbstraite):
    """Vue des options au sujet de l'historique de l'application"""

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        if self.message:
            print(self.message)

    def choisir_menu(self):
        """Insertion du titre recherché"""
        print("\n" + "-" * 50 + "\nRecherhce conversation titre\n" + "-" * 50 + "\n")
        