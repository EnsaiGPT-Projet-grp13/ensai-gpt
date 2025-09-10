from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from view.chatIA_new import ChatNew


class MenuUtilisateurVue(VueAbstraite):
    """
    Menu principal Utilisateur
    """

    def __init__(self, message: str = "") -> None:
        self.message = message

    def afficher(self):
        # optionnel mais utile si ton main appelle afficher()
        if self.message:
            print(self.message)

    def choisir_menu(self):
        # En-tête
        print("\n" + "-" * 50 + "\nMenu Utilisateur\n" + "-" * 50 + "\n")

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

        if choix == "Se déconnecter":
            Session().deconnexion()
            from view.accueil.accueil_vue import AccueilVue
            return AccueilVue("Déconnecté. À bientôt !")

        if choix == "Infos de session":
            return MenuUtilisateurVue(Session().afficher())

        if choix == "Démarrer un chat":
            text = inquirer.text(message="Que veux-tu savoir ?").execute()
            return ChatNew(text)

        if choix == "Reprendre un chat":
            # Si tu n'as pas encore implémenté cette vue, laisse un message, sinon importe-la localement
            # from view.reprendre_chat_vue import ReprendreChatVue
            # return ReprendreChatVue()
            return MenuUtilisateurVue("Reprendre un chat est indisponible pour le moment.")

        # Sécurité : reboucle
        return MenuUtilisateurVue()
