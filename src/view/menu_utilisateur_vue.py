from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session

from view.chatIA_old import OldChat
from view.chatIA_new import ChatNew

class MenuUtilisateurVue(VueAbstraite):
    """
    Menu principal Utilisateur

    - Démarrer un chat : choix d'une personnalité IA puis création d'une nouvelle session
    - Reprendre un chat : lister les sessions existantes de l'utilisateur et en rouvrir une
    - Infos de session : afficher l'utilisateur connecté et la session en cours (si existante)
    - Se déconnecter : retour à l'écran d'accueil
    """

    def __init__(self, message: str = "") -> None:
        self.message = message

    def choisir_menu(self):
        # En-tête
        print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")
        if self.message:
            print(self.message)

        # Choix utilisateur
        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Démarrer un chat",
                "Reprendre un chat",
                "Infos de session",
                "Se déconnecter",
            ],
        ).execute()

        match choix:
            case "Se déconnecter":
                Session().deconnexion()
                from view.accueil.accueil_vue import AccueilVue
                return AccueilVue("Déconnecté. À bientôt !")

            case "Infos de session":
                return MenuUtilisateurVue(Session().afficher())

            case "Démarrer un chat":
                text = inquirer.text(message="Que veux tu savoir?").execute()
                return ChatAIVue(text)

            case "Reprendre un chat":
                return ReprendreChatVue()

        # Sécurité : si aucun match (ne devrait pas arriver), on reboucle
        return MenuUtilisateurVue()
